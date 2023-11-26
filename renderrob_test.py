"""Unit tests for main module."""
import unittest

from PySide6.QtWidgets import QApplication

import renderrob  # type: ignore
from utils import table_utils

# pylint: disable=protected-access


class TestMainWindow(unittest.TestCase):
  """Unit tests for MainWindow."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = renderrob.MainWindow()  # pylint:disable=no-member
    self.main_window.setup()
    table_utils.add_row_below(self.main_window.table)
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
    filepath = "test/test_save_file.rrp"
    self.main_window.open_file(filepath)
    self.assertTrue(filepath in self.main_window.cache.current_file)
    self.assertEqual(self.main_window.cache.current_file, filepath)

  def test_quit(self):
    """Test the quit function."""
    self.main_window.quit()


if __name__ == "__main__":
  unittest.main()
