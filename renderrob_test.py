"""Unit tests for main module."""
import os
import unittest

import renderrob  # type: ignore
from PySide6 import QtTest
from PySide6.QtWidgets import QApplication

from proto import state_pb2
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

  # def test_save_file(self):
  #   """Test the save_file function."""
  #   output_file_path = "test/test_save_file.rrp"
  #   self.main_window.cache.current_file = output_file_path
  #   self.main_window.save_file()
  #   reference_state = state_pb2.render_rob_state()

  #   with open(output_file_path, "rb") as f:
  #     reference_state.ParseFromString(f.read())
  #   self.assertEqual(self.main_window.state, reference_state)

  def test_open_file(self):
    """Test the open_file function."""
    self.main_window.cache.current_file
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
