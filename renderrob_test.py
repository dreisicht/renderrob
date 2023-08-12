"""Unit tests for main module."""
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from PySide6 import QtTest

import renderrob  # type: ignore
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


class TestMainWindow(unittest.TestCase):
  """Unit tests for MainWindow."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = renderrob.MainWindow()
    self.app = self.main_window.setup()
    return super().setUp()

  def test_add_filepath_to_cache(self):
    """Test the add_filepath_to_cache function."""
    self.main_window.add_filepath_to_cache("filepath")
    self.assertTrue(
        "filepath" in self.main_window.cache.recent_files)

  def test_save_as_file(self):
    """Test the save_as_file function."""
    self.main_window.save_as_file()
    self.assertTrue(
        "filepath" in self.main_window.cache.recent_files)

  def test_open_file(self):
    self.main_window.cache.RenderRobCache.current_file


if __name__ == "__main__":
  unittest.main()
