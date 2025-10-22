"""Path utilities."""

import os
from pathlib import Path

# def get_blender_files_path(output_folder: str, path: str) -> str:
#   """Get the blender files path."""
#   common = os.path.commonpath([output_folder, path])
#   combined = os.path.join(output_folder, path)
#   if os.path.exists(combined):
#     return combined
#   return path


def discover_blender_path() -> None:
  """Discover the path to Blender."""
  possibilities = ["C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe",
                   "C:/Program Files/Blender Foundation/Blender/blender.exe",
                   "/Applications/blender/blender.app/Contents/MacOS/blender",
                   "/usr/bin/blender",
                   "/usr/local/bin/blender",
                   "~/blender/"]

  for blender_path in possibilities:
    if os.path.exists(blender_path):
      return blender_path
  return ""


def get_rel_blend_path(blend_path: str, blend_files_dir: str, ) -> str:
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
  if len(path) < 2:
    return path
  path = os.path.normpath(path).replace("\\", "/")
  if path[1] == ":":
    return path[0].upper() + path[1:]
  return path
