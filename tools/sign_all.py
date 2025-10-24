import logging
import os
import subprocess
from pathlib import Path

LOG = logging.getLogger(__name__)

APP_PATH = Path("dist/renderrob.app")
ENTITLEMENTS = Path("tools/entitlements.plist")
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


def sign_filepath(filepath: str | Path) -> None:
  if isinstance(filepath, str):
    filepath = Path(filepath)
  try:
    subprocess.run([*CODESIGN_ARGS, str(filepath)], check=True)
  except subprocess.CalledProcessError as e:
    msg = f"Error signing {filepath}: {e}"
    LOG.exception(msg)


def check_signed(filepath: str | Path) -> None:
  if isinstance(filepath, Path):
    filepath = str(filepath)
  subprocess.run(
    [
      "/usr/bin/codesign",
      "--verify",
      "--strict",
      "--deep",
      "--verbose=2",
      "--entitlements",
      ENTITLEMENTS,
      filepath,
    ],
    check=False,
  )
  subprocess.run(["/usr/sbin/spctl", "--assess", "--type", "execute", "-vv", filepath], check=False)


def main() -> None:
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

  LOG.info("Finished signing.")


if __name__ == "__main__":
  main()
