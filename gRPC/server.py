"""gRPC server bootstrap."""

import logging
import signal
import sys
import os
from concurrent import futures
from typing import Optional

import grpc

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gRPC import vision_pb2, vision_pb2_grpc
from gRPC.servicer import VisionServicer
from Infrastructure.config import Settings, get_settings
from Infrastructure.logger import setup_logger

logger = logging.getLogger("VisionService.gRPC")


def create_server(
    settings: Optional[Settings] = None,
    servicer: Optional[VisionServicer] = None,
) -> grpc.Server:
    settings = settings or get_settings()
    servicer = servicer or VisionServicer(settings=settings)

    max_message = max(settings.GRPC_MAX_MESSAGE_SIZE, settings.MAX_FILE_SIZE + 1024 * 1024)

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.GRPC_MAX_WORKERS),
        maximum_concurrent_rpcs=settings.GRPC_MAX_WORKERS * 4,
        options=[
            ("grpc.max_receive_message_length", max_message),
            ("grpc.max_send_message_length", max_message),
            ("grpc.keepalive_time_ms", 60_000),
            ("grpc.keepalive_timeout_ms", 20_000),
        ],
    )
    vision_pb2_grpc.add_VisionServiceServicer_to_server(servicer, server)

    if settings.GRPC_ENABLE_REFLECTION:
        try:
            from grpc_reflection.v1alpha import reflection
            reflection.enable_server_reflection(
                (
                    vision_pb2.DESCRIPTOR.services_by_name["VisionService"].full_name,
                    reflection.SERVICE_NAME,
                ),
                server,
            )
        except ImportError:
            logger.warning("grpcio-reflection not installed; reflection disabled")

    address = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    bound = server.add_insecure_port(address)
    if bound == 0:
        raise RuntimeError(f"gRPC could not bind to {address}")

    logger.info(f"gRPC server bound on {address} (workers={settings.GRPC_MAX_WORKERS})")
    return server


def start_grpc_server(settings: Optional[Settings] = None) -> grpc.Server:
    server = create_server(settings)
    server.start()
    logger.info("gRPC server started")
    return server


def serve() -> None:
    setup_logger("VisionService.gRPC")
    settings = get_settings()

    # ---- Warm up models BEFORE starting the server ----
    logger.info("Loading models...")
    try:
        from Core.model import model as main_model
        from Core.binary_model import binary_classifier

        logger.info(f"  Main model   : {'loaded' if main_model is not None else 'NOT loaded'}")
        logger.info(f"  Binary model : {'loaded' if binary_classifier.model is not None else 'NOT loaded'}")

        if main_model is not None:
            import numpy as np
            logger.info("  Warming up inference graph...")
            dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
            main_model.predict(dummy, verbose=0)
            logger.info("  Inference graph warm")
    except Exception as exc:
        logger.warning(f"Warm-up failed (service will still start): {exc}")

    # ---- Start the server ----
    server = start_grpc_server(settings)

    def _stop(signum, _frame):
        logger.info(f"Signal {signum} received, stopping gRPC server...")
        server.stop(settings.GRPC_SHUTDOWN_GRACE)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    server.wait_for_termination()
    logger.info("gRPC server stopped")


if __name__ == "__main__":
    serve()