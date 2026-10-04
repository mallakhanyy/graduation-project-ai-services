"""Regenerate gRPC stubs from Protos/vision.proto."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = ROOT / "Protos"
OUT_DIR = ROOT / "gRPC"


def main() -> int:
    from grpc_tools import protoc

    code = protoc.main([
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--pyi_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        str(PROTO_DIR / "vision.proto"),
    ])
    if code != 0:
        print("protoc failed", file=sys.stderr)
        return code

    grpc_file = OUT_DIR / "vision_pb2_grpc.py"
    text = grpc_file.read_text(encoding="utf-8")
    text = re.sub(r"^import vision_pb2 as", "from gRPC import vision_pb2 as", text, flags=re.M)
    grpc_file.write_text(text, encoding="utf-8")

    print("Generated stubs in", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())