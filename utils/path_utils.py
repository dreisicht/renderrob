"""Path utilities."""

import os


def get_blender_files_path(output_folder: str, path: str) -> str:
  """Get the blender files path."""
  combined = os.path.join(output_folder, path)
  if os.path.exists(combined):
    return combined
  return path


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


def get_blend_path(blend_path: str, blender_files_path: str) -> str:
  """Get the absolute path of the blend file."""
  if os.path.basename(blend_path) == blend_path:
    return os.path.join(blender_files_path, blend_path)
  return blend_path
