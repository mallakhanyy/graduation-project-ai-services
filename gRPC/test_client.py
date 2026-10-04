"""gRPC Test Client — tests multiple images against the service."""

import grpc
import time
import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gRPC import vision_pb2, vision_pb2_grpc


TEST_IMAGES = [
    {
        "name": "Pipe Damage",
        "url": "http://localhost:9000/WahaKun/waha_dataset/Pipe_Damage/image7pipe.jpg",
        "expected": "Pipe_Damage",
    },
    {
        "name": "Overflow",
        "url": "http://localhost:9000/WahaKun/waha_dataset/Overflow/image2overflow.jpg",
        "expected": "Overflow",
    },
    {
        "name": "Blockage",
        "url": "http://localhost:9000/WahaKun/waha_dataset/Blockage/image33bock.jpg",
        "expected": "Blockage",
    },
    {
        "name": "Unknown 1 (OIP 2)",
        "url": "http://localhost:9000/test_images_new/OIP%20(2).webp",
        "expected": "FAILED_PRECONDITION / INVALID_ARGUMENT",
    },
    {
        "name": "Unknown 2 (OIP 3)",
        "url": "http://localhost:9000/test_images_new/OIP%20(3).webp",
        "expected": "FAILED_PRECONDITION / INVALID_ARGUMENT",
    },
    {
        "name": "Unknown 3 (OIP 4)",
        "url": "http://localhost:9000/test_images_new/OIP%20(4).webp",
        "expected": "FAILED_PRECONDITION / INVALID_ARGUMENT",
    },
]


def print_success(i, name, expected, response, elapsed):
    print("=" * 70)
    print(f"[{i}] {name}")
    print(f"    Expected : {expected}")
    print("-" * 70)
    print(f"    Status         : {response.status}")
    print(f"    Problem        : {response.problem}")
    print(f"    Confidence     : {response.confidence}")
    print(f"    Severity       : {response.severity}")
    print(f"    Recommendation : {response.recommendation}")
    print(f"    Explanation    : {response.explanation}")
    print(f"    Repair Steps   :")
    for n, step in enumerate(response.repair_steps, 1):
        print(f"      {n}. {step}")
    print(f"    Timestamp      : {response.timestamp}")
    print(f"    Response time  : {elapsed:.2f}s")
    print("=" * 70)
    print()


def print_error(i, name, expected, rpc_error, elapsed):
    print("=" * 70)
    print(f"[{i}] {name}")
    print(f"    Expected : {expected}")
    print("-" * 70)
    print(f"    RPC Error      : {rpc_error.code().name}")
    print(f"    Detail         : {rpc_error.details()}")
    print(f"    Response time  : {elapsed:.2f}s")
    print("=" * 70)
    print()


def main():
    channel = grpc.insecure_channel(
        "localhost:50051",
        options=[
            ("grpc.max_receive_message_length", 16 * 1024 * 1024),
            ("grpc.max_send_message_length", 16 * 1024 * 1024),
        ],
    )
    stub = vision_pb2_grpc.VisionServiceStub(channel)

    print()
    print("=" * 70)
    print("  gRPC Vision Service - Test Suite")
    print("=" * 70)
    print(f"  Server : localhost:50051")
    print(f"  Images : {len(TEST_IMAGES)}")
    print("=" * 70)
    print()

    try:
        h = stub.HealthCheck(vision_pb2.HealthRequest(), timeout=60.0)
        print(f"  Health  : {h.status}")
        print(f"  Service : {h.service} v{h.version}")
        print(f"  Model   : {'loaded' if h.model_loaded else 'NOT loaded'}")
        print("=" * 70)
        print()
    except grpc.RpcError as e:
        print(f"  HealthCheck failed: {e.code().name}: {e.details()}")
        print()

    results = []

    for i, img in enumerate(TEST_IMAGES, 1):
        request = vision_pb2.PredictRequest(
            request_id=f"test-{i}",
            image_url=img["url"],
        )

        start = time.time()
        try:
            response = stub.Predict(request, timeout=60.0)
            elapsed = time.time() - start
            print_success(i, img["name"], img["expected"], response, elapsed)
            results.append((img["name"], "success", True, elapsed))

        except grpc.RpcError as e:
            elapsed = time.time() - start
            print_error(i, img["name"], img["expected"], e, elapsed)
            results.append((img["name"], e.code().name, False, elapsed))

    print()
    print("=" * 70)
    print("  Test Summary")
    print("=" * 70)
    for name, status, ok, elapsed in results:
        icon = "[OK]" if ok else "[ERR]"
        print(f"  {icon} {name:30s} | {status:20s} | {elapsed:.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()