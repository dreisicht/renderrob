# https://just.systems

default: check

run:
    cd src && uv run python main.py

# protoc comes from grpcio-tools in the dev group, so no system protoc is needed. --pyi_out gives
# the generated modules type stubs; without them a type checker sees the message classes as
# missing, since protobuf builds them at runtime from the descriptor pool.

protos:
    uv run --group dev python -m grpc_tools.protoc \
        --proto_path=src/protos --python_out=src/protos --pyi_out=src/protos \
        src/protos/state.proto src/protos/cache.proto

test:
    cd src && QT_QPA_PLATFORM=offscreen uv run python -m unittest discover -s . -p '*_test.py'

lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check

format:
    uv run ruff format .

check: lint test

bundle:
    uv sync --group build
    uv run pyinstaller --noconfirm --clean tools/renderrob.spec

build_mac:
    sh tools/build_mac.sh

update:
    uv lock --upgrade
