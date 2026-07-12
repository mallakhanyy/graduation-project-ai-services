"""
app.py
------
FastAPI application entrypoint for the ASR Service.

Responsibilities:
- Create and configure the FastAPI app
- Wire in the request-tracking middleware (X-Request-ID)
- Start/stop the RabbitMQ connection and the background job consumer
- Register a global error handler so failures never leak raw tracebacks

This file should NOT:
- Contain route logic (routes.py)
- Contain model logic (model.py)
- Contain RabbitMQ plumbing (queue_broker.py)
"""

import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config import settings
from logger import logger
from queue_broker import broker
from routes import router
from schemas import ErrorResponse, Metadata
from worker import process_transcription_job


async def _consume_forever() -> None:
    """Wraps the queue consumer so a single bad message can't kill the
    background task silently — it logs and keeps listening."""
    try:
        await broker.consume_requests(_handle_job)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.critical(f"Job consumer stopped unexpectedly: {e}")


async def _handle_job(payload: dict) -> None:
    result = await process_transcription_job(payload)
    await broker.publish_result(result.model_dump())


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    consumer_task = asyncio.create_task(_consume_forever())

    logger.info(f"{settings.service.name} started on {settings.server.host}:{settings.server.port}.")

    yield

    consumer_task.cancel()
    await asyncio.gather(consumer_task, return_exceptions=True)
    await broker.close()
    logger.info(f"{settings.service.name} stopped.")


app = FastAPI(
    title=settings.service.name,
    description=settings.service.description,
    version=settings.service.version,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Honors an inbound X-Request-ID from the .NET backend, or generates
    one for local/Swagger testing, per the platform's request-tracking
    standard."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"RequestID={request_id} | Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error.",
            metadata=Metadata(request_id=request_id),
        ).model_dump(),
    )


app.include_router(router)