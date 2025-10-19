import os
import subprocess
from pathlib import Path

APP_PATH = Path("dist/renderrob.app")
CODESIGN_ARGS = [
    "codesign",
    "-s",
    "5K24F4J2M5",
    "-f",
    "--timestamp",
    "-o",
    "runtime",
    "-i",
    "com.dreisicht.renderrob",
]
SIGNABLE_EXTENSIONS = {
    ".dylib",
    ".so",
    ".node",
    ".app",
    ".framework",
    ".a",
    ".xpc",
    ".appex",
    "",
}


def sign_filepath(filepath):
    if isinstance(filepath, str):
        filepath = Path(filepath)
    # print(f"Signing {filepath}")
    try:
        subprocess.run(CODESIGN_ARGS + [str(filepath)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error signing {filepath}: {e}")


def check_signed(filepath):
    if isinstance(filepath, Path):
        filepath = str(filepath)
    subprocess.run(
        ["codesign", "--verify", "--strict", "--deep", "--verbose=2", filepath]
    )
    subprocess.run(["spctl", "--assess", "--type", "execute", "-vv", filepath])


def main():
    for root, dirs, files in os.walk(APP_PATH, topdown=False):
        root_ = Path(root)
        for name in files:
            if name == "renderrob":
                sign_filepath(root_ / name)
            if Path(name).suffix not in SIGNABLE_EXTENSIONS:
                continue
            sign_filepath(root_ / name)
        for name in dirs:
            sign_filepath(root_ / name)

    sign_filepath(APP_PATH)

    print("Finished signing.")


if __name__ == "__main__":
    main()
