#!/bin/sh
# Generate the Python bindings for the Render Rob protos.
# protoc comes from grpcio-tools (dev dependency group), so no system protoc is needed.
set -e
PROTOS_DIR=src/protos

# --pyi_out gives the generated modules type stubs; without them a type checker sees the message
# classes as missing, since protobuf builds them at runtime from the descriptor pool.
uv run --group dev python -m grpc_tools.protoc \
  --proto_path="$PROTOS_DIR" --python_out="$PROTOS_DIR" --pyi_out="$PROTOS_DIR" \
  "$PROTOS_DIR/state.proto" "$PROTOS_DIR/cache.proto"
