PROTOS_DIR=src/protos

uv run protoc --proto_path=$PROTOS_DIR --python_out=$PROTOS_DIR $PROTOS_DIR/state.proto
uv run protoc --proto_path=$PROTOS_DIR --python_out=$PROTOS_DIR $PROTOS_DIR/cache.proto
