"""Settings dialog for RenderRob."""

from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader

import utils.ui_utils as ui_utils
from state_saver import STATESAVER


class SettingsWindow():
  """Settings dialog for RenderRob."""

  def __init__(self) -> None:
    """Open the settings dialog."""
    self.window = ui_utils.load_ui_from_file("ui/settings.ui")
    # Load state into the settings dialog.
    self.make_settings_window_connections(self.window)

    self.window.lineEdit_3.setText(STATESAVER.state.settings.blender_path)
    self.window.lineEdit_2.setText(STATESAVER.state.settings.output_path)
    self.window.lineEdit.setText(STATESAVER.state.settings.blender_files_path)

    self.window.checkBox_2.setCheckState(
        Qt.Checked if STATESAVER.state.settings.preview.samples_use else Qt.Unchecked)
    self.window.checkBox_3.setCheckState(
        Qt.Checked if STATESAVER.state.settings.preview.frame_step_use else Qt.Unchecked)
    self.window.checkBox.setCheckState(
        Qt.Checked if STATESAVER.state.settings.preview.resolution_use else Qt.Unchecked)

    self.window.spinBox_3.setValue(
        int(STATESAVER.state.settings.preview.samples))
    self.window.spinBox_2.setValue(
        int(STATESAVER.state.settings.preview.frame_step))
    self.window.spinBox.setValue(
        int(STATESAVER.state.settings.preview.resolution))

    self.window.lineEdit_4.setText(
        ";".join(STATESAVER.state.settings.addons))

    self.window.exec()

  def make_settings_window_connections(self, window: QUiLoader) -> None:
    """Make connections for buttons in settings dialog.."""
    window.buttonBox.accepted.connect(self.save_settings_state)

  def save_settings_state(self) -> None:
    """Save the state from the settings dialog into the global state."""
    STATESAVER.state.settings.blender_path = self.window.lineEdit_3.text()
    STATESAVER.state.settings.output_path = self.window.lineEdit_2.text()
    STATESAVER.state.settings.blender_files_path = self.window.lineEdit.text()

    STATESAVER.state.settings.preview.samples_use = self.window.checkBox_2.isChecked()
    STATESAVER.state.settings.preview.frame_step_use = self.window.checkBox_3.isChecked()
    STATESAVER.state.settings.preview.resolution_use = self.window.checkBox.isChecked()

    # Check if the values are empty, if so, set them to 0.
    samples = self.window.spinBox_3.cleanText()
    STATESAVER.state.settings.preview.samples = int(samples) if samples else 0
    frame_step = self.window.spinBox_2.cleanText()
    STATESAVER.state.settings.preview.frame_step = int(
        frame_step) if frame_step else 0
    resolution = self.window.spinBox.cleanText()
    STATESAVER.state.settings.preview.resolution = int(
        resolution) if resolution else 0

    del STATESAVER.state.settings.addons[:]
    addons_str = self.window.lineEdit_4.text()
    for addon in addons_str.split(";"):
      STATESAVER.state.settings.addons.append(addon)
