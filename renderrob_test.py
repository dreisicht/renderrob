"""Unit tests for main module."""
import unittest

import renderrob  # type: ignore
from PySide6 import QtTest
from PySide6.QtWidgets import QApplication


class TestMainWindow(unittest.TestCase):
  """Unit tests for MainWindow."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = renderrob.MainWindow()
    self.main_window.setup()
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
    self.main_window.add_filepath_to_cache("filepath")
    self.assertTrue(
        "filepath" in self.main_window.cache.recent_files)

  # def test_save_as_file(self):
  #   """Test the save_as_file function."""
  #   self.main_window.save_as_file()
  #   self.assertTrue(
  #       "filepath" in self.main_window.cache.recent_files)

  def test_open_file(self):
    """Test the open_file function."""
    self.main_window.cache.current_file


if __name__ == "__main__":
  unittest.main()
