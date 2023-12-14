import unittest

from utils_rr import path_utils


class TestPathUtils(unittest.TestCase):

  def test_normalize_drive_letter(self):
    """Test that the drive letter is normalized correctly."""
    self.assertEqual(path_utils.normalize_drive_letter(
        "c:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py"),
        "C:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py")
    self.assertEqual(path_utils.normalize_drive_letter(
        "d:/test/file.txt"),
        "D:/test/file.txt")
    self.assertEqual(path_utils.normalize_drive_letter(
        "e:\\test\\file.txt"),
        "E:/test/file.txt")
    self.assertEqual(path_utils.normalize_drive_letter(
        "\\\\server\\share\\file.txt"),
        "//server/share/file.txt")
    self.assertEqual(path_utils.normalize_drive_letter("a"), "a")

  def test_get_rel_blend_path(self):
    """Test that the relative path to the blend file is correct."""
    self.assertEqual(path_utils.get_rel_blend_path(
        "C:/Users/peter/Nextcloud/20_prod/24_shots/SH050/SH050_render.blend",
        "C:/Users/peter/Nextcloud/20_prod/24_shots"),
        "SH050\\SH050_render.blend")
    self.assertEqual(path_utils.get_rel_blend_path('C:/something/completely/different.blend',
                                                   "C:/Users/peter/Nextcloud/20_prod/24_shots"
                                                   ), 'C:/something/completely/different.blend')
    self.assertEqual(path_utils.get_rel_blend_path('different.blend',
                                                   "C:/Users/peter/Nextcloud/20_prod/24_shots"
                                                   ), 'different.blend')

  def test_get_abs_blend_path(self):
    self.assertEqual(path_utils.get_abs_blend_path(
        'SH050\\SH050_render.blend', 'C:/Users/peter/Nextcloud/20_prod/24_shots'),
        'C:\\Users\\peter\\Nextcloud\\20_prod\\24_shots\\SH050\\SH050_render.blend')

    self.assertEqual(path_utils.get_abs_blend_path(
        'C:/something/completely/different.blend', 'C:/Users/peter/Nextcloud/20_prod/24_shots'),
        'C:/something/completely/different.blend')
