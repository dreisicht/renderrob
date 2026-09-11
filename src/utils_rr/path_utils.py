"""Path utilities."""

import os
from pathlib import Path


def discover_blender_path() -> str:
  """Discover the path to Blender."""
  possibilities = [
    "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe",
    "C:/Program Files/Blender Foundation/Blender/blender.exe",
    "/Applications/Blender.app/Contents/MacOS/Blender",
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "~/blender/blender",
  ]

  for blender_path in possibilities:
    blender_path_path = Path(blender_path).expanduser()
    if blender_path_path.exists() and blender_path_path.is_file():
      return blender_path
  return ""


def get_rel_blend_path(blend_path: str, blend_files_dir: str) -> str:
  """Get the blender files path."""
  if not Path(blend_path).is_absolute():
    return os.path.normpath(blend_path).strip()
  common = os.path.normpath(os.path.commonpath([blend_path, blend_files_dir]))
  if os.path.normpath(blend_files_dir) not in common:
    return os.path.normpath(blend_path).strip()
  return os.path.relpath(blend_path, blend_files_dir)


def get_abs_blend_path(blend_path: str, blend_files_dir: str) -> str:
  """Get the absolute path of the blend file."""
  if Path(blend_path).is_absolute():
    return blend_path
  return str(Path(blend_files_dir) / blend_path)


def normalize_drive_letter(path: str) -> str:
  """Normalize the drive letter to upper case."""
  min_len = 2
  if len(path) < min_len:
    return path
  path = os.path.normpath(path).replace("\\", "/")
  if path[1] == ":":
    return path[0].upper() + path[1:]
  return path


def get_resource_root() -> Path:
  """Return the directory holding Render Rob's own data: ui/, icon/, utils_bpy/, utils_common/.

  Where that is depends on how Render Rob was started. In a py2app bundle they are copied next to
  the executable, under ../Resources. In a PyInstaller bundle - and in a source checkout - they
  sit beside this module's package, one level above this file. Checking for utils_bpy rather than
  asking for the current working directory keeps this correct however Render Rob was started, and
  independent of where it was started from.
  """
  bundle_resources = Path("../Resources")
  if (bundle_resources / "utils_bpy").is_dir():
    return bundle_resources
  return Path(__file__).parent.parent


def get_blender_module_path() -> str:
  """Return the directory Blender has to put on sys.path to import Render Rob's bpy helpers."""
  return normalize_drive_letter(str(get_resource_root().resolve()))
