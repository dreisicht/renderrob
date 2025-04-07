import subprocess
from pathlib import Path

SIGNING_PROCESS = (
    'codesign -s "Peter Baintner" -f --timestamp -i "com.dreisicht.renderrob" --deep '
)


def do_signing_recursively():
    base_path = "/tmp/renderrob_testing/RenderRob.app"
    for filepath in Path(base_path).rglob("*"):
        if filepath.is_dir():
            continue
        if not filepath.suffix == ".dylib":
            continue
        print(str(filepath))
        subprocess.call(SIGNING_PROCESS + str(filepath), shell=True)


if __name__ == "__main__":
    do_signing_recursively()
