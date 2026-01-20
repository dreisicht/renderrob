"""Tests for the path utilities."""

import platform
import unittest

from utils_rr import path_utils


class TestPathUtils(unittest.TestCase):
  """Test for the path utilities."""

  @unittest.skipIf(platform.system() != "Windows", "Test only works on Windows.")
  def test_normalize_drive_letter(self) -> None:
    """Test that the drive letter is normalized correctly."""
    self.assertEqual(
      path_utils.normalize_drive_letter(
        "c:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py",
      ),
      "C:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py",
    )
    self.assertEqual(path_utils.normalize_drive_letter("d:/test/file.txt"), "D:/test/file.txt")
    self.assertEqual(path_utils.normalize_drive_letter("e:\\test\\file.txt"), "E:/test/file.txt")
    self.assertEqual(
      path_utils.normalize_drive_letter("\\\\server\\share\\file.txt"), "//server/share/file.txt",
    )
    self.assertEqual(path_utils.normalize_drive_letter("a"), "a")

  @unittest.skipIf(platform.system() != "Windows", "Test only works on Windows.")
  def test_get_rel_blend_path(self) -> None:
    """Test that the relative path to the blend file is correct."""
    path = path_utils.get_rel_blend_path(
      "C:/Users/peter/Nextcloud/20_prod/24_shots/SH050/SH050_render.blend",
      "C:/Users/peter/Nextcloud/20_prod/24_shots",
    )
    self.assertEqual(path, "SH050\\SH050_render.blend")

    path = path_utils.get_rel_blend_path(
      "C:/something/completely/different.blend", "C:/Users/peter/Nextcloud/20_prod/24_shots",
    )
    self.assertEqual(path.replace("\\", "/"), "C:/something/completely/different.blend")

    path = path_utils.get_rel_blend_path(
      "different.blend", "C:/Users/peter/Nextcloud/20_prod/24_shots",
    )
    self.assertEqual(path, "different.blend")

  @unittest.skipIf(platform.system() != "Windows", "Test only works on Windows.")
  def test_get_abs_blend_path(self) -> None:
    """Test that the absolute path to the blend file is correct."""
    path = path_utils.get_abs_blend_path(
      "SH050\\SH050_render.blend", "C:/Users/peter/Nextcloud/20_prod/24_shots",
    )
    self.assertEqual(
      path.replace("\\", "/"), "C:/Users/peter/Nextcloud/20_prod/24_shots/SH050/SH050_render.blend",
    )

    path = path_utils.get_abs_blend_path(
      "C:/something/completely/different.blend", "C:/Users/peter/Nextcloud/20_prod/24_shots",
    )
    self.assertEqual(path.replace("\\", "/"), "C:/something/completely/different.blend")
