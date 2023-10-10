"""Unit tests for table_utils.py."""
import table_utils
import unittest


class TestTableUtils(unittest.TestCase):
  """Tests for the table_utils module."""

  def test_normalize_drive_letter(self):
    """Test that the drive letter is normalized correctly."""
    self.assertEqual(table_utils.normalize_drive_letter(
        "c:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py"),
        "C:/Users/peter/Documents/repositories/RenderRob/render_job_to_rss.py")
    self.assertEqual(table_utils.normalize_drive_letter(
        "d:/test/file.txt"),
        "D:/test/file.txt")
    self.assertEqual(table_utils.normalize_drive_letter(
        "e:\\test\\file.txt"),
        "E:/test/file.txt")
    self.assertEqual(table_utils.normalize_drive_letter(
        "\\\\server\\share\\file.txt"),
        "//server/share/file.txt")
