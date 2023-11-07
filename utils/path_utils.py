"""Path utilities."""

import os


def get_blender_files_path(output_folder: str, path: str) -> str:
  """Get the blender files path."""
  # TODO: Add test.
  combined = os.path.join(output_folder, path)
  if os.path.exists(combined):
    return combined
  return path
