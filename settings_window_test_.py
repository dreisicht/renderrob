"""Tests for settings_window.py."""
import sys
import unittest

from PySide6.QtWidgets import QApplication

import settings_window


class SettingsWindowTest(unittest.TestCase):
  """Tests for the settings window."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.app = QApplication(sys.argv)
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests."""
    app_instance = QApplication.instance()
    app_instance.shutdown()
    del app_instance
    return super().tearDown()

  # def test_load_state_into_settings_dialog(self) -> None:
  #   """Test that the state is loaded into the settings dialog correctly."""
  #   window = settings_window.SettingsWindow()

  #   self.assertEqual(
  #       window.window.lineEdit_3.text(), "/path/to/blender")
  #   self.assertEqual(
  #       window.window.lineEdit_2.text(), "/path/to/output")
  #   self.assertEqual(
  #       window.window.lineEdit.text(), "/path/to/blender_files")
  #   self.assertTrue(window.window.checkBox_2.isChecked())
  #   self.assertTrue(window.window.checkBox_3.isChecked())
  #   self.assertTrue(window.window.checkBox.isChecked())
  #   self.assertEqual(
  #       window.window.spinBox_3.value(), 100)
  #   self.assertEqual(
  #       window.window.spinBox_2.value(), 2)
  #   self.assertEqual(
  #       window.window.spinBox.value(), 1080)
  #   self.assertEqual(
  #       window.window.lineEdit_4.text(), "addon1;addon2")

  # def test_save_settings_state(self) -> None:
  #   """Test that the state is saved from the settings dialog correctly."""
  #   state = {}
  #   window = settings_window.SettingsWindow()
  #   window.save_settings_state()

  #   self.assertEqual(
  #       state["blender_path"], "")
  #   self.assertEqual(
  #       state["output_path"], "")
  #   self.assertEqual(
  #       state["blender_files_path"], "")
  #   self.assertEqual(state["preview"], {})
  #   self.assertEqual(state["addons"], [])

  # def test_make_settings_window_connections(self) -> None:
  #   """Test that the connections are made correctly."""
  #   window = settings_window.SettingsWindow()
  #   window.make_settings_window_connections(window.window)

  #   self.assertTrue(
  #       window.window.buttonBox.accepted.connect(window.save_settings_state))

  # def test_discover_blender_path(self) -> None:
  #   """Test that the blender path is discovered correctly."""
  #   window = settings_window.SettingsWindow()
  #   window.discover_blender_path()

  #   self.assertEqual(
  #       window.window.lineEdit_3.text(),
  #       "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe")


if __name__ == "__main__":
  unittest.main()
