"""Unit tests for main module."""
import os
import unittest

from PySide6.QtWidgets import QApplication

import renderrob  # type: ignore
from utils import table_utils


class TestMainWindow(unittest.TestCase):
  """Unit tests for MainWindow."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = renderrob.MainWindow()
    self.main_window.setup()
    table_utils.add_row_below()
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests."""
    app_instance = QApplication.instance()
    app_instance.shutdown()
    del app_instance
    del self.main_window.app
    del self.main_window
    return super().tearDown()

  def test_add_filepath_to_cache(self):
    """Test the add_filepath_to_cache function."""
    self.main_window.add_filepath_to_cache("test/test_save_file.rrp")
    self.assertTrue(
        "test/test_save_file.rrp" in self.main_window.cache.recent_files)

  def test_new_file(self):
    """Test the new_file function."""
    self.main_window.new_file()

  def test_open_file(self):
    """Test the open_file function."""
    self.assertTrue("test/test_save_file.rrp" in self.main_window.cache.current_file)
    abs_path = os.path.abspath("test/test_save_file.rrp").replace("\\", "/")
    self.assertTrue(abs_path.lower() in self.main_window.cache.recent_files[0].lower())

  def test_quit(self):
    """Test the quit function."""
    self.main_window.quit()

  def test_open_recent_file(self):
    """Test the open_recent_file function."""
    self.main_window.open_recent_file0()


if __name__ == "__main__":
  unittest.main()
