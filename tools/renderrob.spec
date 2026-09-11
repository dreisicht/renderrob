# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the downloadable Render Rob bundles.

One spec serves all three platforms; the release workflow runs `pyinstaller tools/renderrob.spec`
unchanged on Linux, macOS and Windows and only differs in how it archives the result.

Two things here are load-bearing rather than cosmetic:

  * The build is onedir, not onefile. Render Rob hands the directory holding `utils_bpy` to a
    separate Blender process (see path_utils.get_resource_root), and a onefile build unpacks that
    directory into a temporary folder that is deleted the moment Render Rob exits.
  * ui/, icon/, utils_bpy/ and utils_common/ are collected as plain files rather than left to the
    module analysis. Blender imports the last two with its own interpreter, off disk, so they have
    to exist as readable .py next to the executable - inside the frozen archive is useless to it.
    This mirrors DATA_FILES in the py2app setup.py.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(SPECPATH).parent  # noqa: F821  # PyInstaller injects SPECPATH.
SRC = REPO_ROOT / "src"

# Copied whole, under the names the app imports and opens them by, so they stay flat at the
# bundle root. A developer's __pycache__ is left behind: Blender runs a different Python than the
# one that wrote it, and shipping bytecode nothing can load only makes the download bigger.
DATA_DIRS = ["ui", "icon", "utils_bpy", "utils_common"]


# src/version.py is a single assignment, so reading it beats importing it - the spec runs under
# PyInstaller's interpreter, which has never seen src/ on its path.
version = SRC.joinpath("version.py").read_text(encoding="utf-8").split('"')[1]

# Only Windows takes the icon from the executable itself; macOS takes it from the .app below and
# Linux has no equivalent, where passing one only produces a warning.
exe_icon = [str(SRC / "icon" / "icon.ico")] if sys.platform == "win32" else None

a = Analysis(  # noqa: F821
  [str(SRC / "main.py")],
  # src/ is not a package: the app imports its own modules as top-level names (`import
  # settings_window`, `from utils_rr import ...`), exactly as the test runner does.
  pathex=[str(SRC)],
  binaries=[],
  # The data directories are appended below instead, because Tree() yields entries in the
  # three-part form Analysis takes only after it has normalised its own `datas`.
  datas=[],
  hiddenimports=[],
  hookspath=[],
  hooksconfig={},
  runtime_hooks=[],
  excludes=[
    # bpy is a ~1 GB dependency that only ever runs inside the user's own Blender, never inside
    # Render Rob. Nothing main.py imports reaches it, but excluding it makes that a build error
    # rather than a gigabyte-sized surprise if that ever changes.
    "bpy",
    "tkinter",
    "unittest",
  ],
  noarchive=False,
  optimize=0,
)
for name in DATA_DIRS:
  a.datas += Tree(str(SRC / name), prefix=name, excludes=["__pycache__"])  # noqa: F821

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
  pyz,
  a.scripts,
  [],
  exclude_binaries=True,
  name="renderrob",
  debug=False,
  bootloader_ignore_signals=False,
  strip=False,
  # UPX is not installed on the runners, and compressing Qt's libraries has a history of
  # producing binaries that fail to start.
  upx=False,
  # Render Rob prints Blender's output into its own console widget, so it needs no terminal.
  console=False,
  disable_windowed_traceback=False,
  argv_emulation=False,
  target_arch=None,
  codesign_identity=None,
  entitlements_file=None,
  icon=exe_icon,
)
coll = COLLECT(  # noqa: F821
  exe,
  a.binaries,
  a.datas,
  strip=False,
  upx=False,
  upx_exclude=[],
  name="renderrob",
)

# macOS only: wrap the collected directory in the .app that Finder and `open` expect. PyInstaller
# ignores this on the other platforms.
app = BUNDLE(  # noqa: F821
  coll,
  name="RenderRob.app",
  icon=str(SRC / "icon" / "icon.icns"),
  bundle_identifier="com.dreisicht.renderrob",
  info_plist={
    "CFBundleName": "Render Rob",
    "CFBundleDisplayName": "Render Rob",
    "CFBundleShortVersionString": version,
    "CFBundleVersion": version,
    "NSHighResolutionCapable": True,
    # Render Rob starts Blender, which renders to wherever the user pointed it.
    "LSEnvironment": {"PYTHONOPTIMIZE": "1"},
  },
)
