"""Settings dialog for RenderRob."""

# import appdirs
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog

from proto import state_pb2
from utils import ui_utils

# class SettingsHandler():
#   """Class to handle the storage of the settings."""

#   def __init__(self) -> None:
#     self.settings_path = os.path.join(self.get_settings_output_dir(), ".rr_settings")
#     print_utils.print_info("The settings are stored in: " + self.settings_path)

#   def get_settings(self) -> None:
#     """Get the settings from the settings file if existing."""
#     settings_state = settings_pb2.settings()  # pylint: disable=no-member
#     if os.path.exists(self.settings_path):
#       with open(self.settings_path, "rb") as settings_file:
#         settings_state.ParseFromString(settings_file.read())
#     return settings_state  # pylint: disable=no-member

#   def save_settings(self, settings_state: settings_pb2) -> None:
#     """Save the settings to the settings file."""
#     with open(self.settings_path, "wb") as settings_file:
#       settings_file.write(settings_state.SerializeToString())

#   def get_settings_output_dir(self) -> str:
#     """Get the output directory from the settings."""
#     data_dir = os.path.join(appdirs.AppDirs().user_data_dir, "RenderRob")
#     if not os.path.exists(data_dir):
#       os.makedirs(data_dir)
#     return data_dir


class SettingsWindow():
  """Settings dialog for RenderRob.

  This class represents a settings dialog for RenderRob. It allows the user to modify various
  settings such as the path to Blender, output path, Blender files path, and more. The class also
  provides methods to save the state from the settings dialog into the global state.
  """

  def __init__(self, state: state_pb2.render_rob_state) -> None:  # pylint: disable=no-member
    """Open the settings dialog."""
    self.state = state.settings
    self.window = ui_utils.load_ui_from_file("ui/settings.ui")
    self.window.setWindowTitle("RenderRob Settings")
    self.window.setWindowIcon(QIcon("icons/icon.ico"))
    # Load state into the settings dialog.
    self.make_settings_window_connections(self.window)

    self.window.lineEdit_3.setText(self.state.blender_path)
    self.window.lineEdit_2.setText(self.state.output_path)
    self.window.lineEdit.setText(self.state.blender_files_path)

    self.window.checkBox_2.setCheckState(
        Qt.Checked if self.state.preview.samples_use else Qt.Unchecked)
    self.window.checkBox_3.setCheckState(
        Qt.Checked if self.state.preview.frame_step_use else Qt.Unchecked)
    self.window.checkBox.setCheckState(
        Qt.Checked if self.state.preview.resolution_use else Qt.Unchecked)

    self.window.spinBox_3.setValue(int(self.state.preview.samples))
    self.window.spinBox_2.setValue(int(self.state.preview.frame_step))
    self.window.spinBox.setValue(int(self.state.preview.resolution))
    self.window.spinBox_4.setValue(int(self.state.fps))

    self.window.lineEdit_4.setText(";".join(self.state.addons))

    self.window.exec()

  def make_settings_window_connections(self, window: QUiLoader) -> None:
    """Make connections for buttons in settings dialog.."""
    window.buttonBox.accepted.connect(self.save_settings_state)
    window.blender_button.clicked.connect(self.open_blender_path)
    window.files_button.clicked.connect(self.open_blender_files_path)
    window.output_button.clicked.connect(self.open_output_path)

  def open_blender_path(self) -> None:
    """Open a file dialog to select the path to Blender."""
    path = QFileDialog.getOpenFileName(
        self.window, caption="Select Blender Path", filter="Blender (*.exe)")
    if path:
      self.window.lineEdit_3.setText(path[0])

  def open_blender_files_path(self) -> None:
    """Open a file dialog to select the path to Blender files."""
    path = QFileDialog.getExistingDirectory(self.window, caption="Select Blender Files Path")
    if path:
      self.window.lineEdit.setText(path)

  def open_output_path(self) -> None:
    """Open a file dialog to select the output path."""
    path = QFileDialog.getExistingDirectory(self.window, caption="Select Output Path")
    if path:
      self.window.lineEdit_2.setText(path)

  def save_settings_state(self) -> None:
    """Save the state from the settings dialog into the global state."""
    self.state.blender_path = self.window.lineEdit_3.text()
    self.state.output_path = self.window.lineEdit_2.text()
    self.state.blender_files_path = self.window.lineEdit.text()

    self.state.preview.samples_use = self.window.checkBox_2.isChecked()
    self.state.preview.frame_step_use = self.window.checkBox_3.isChecked()
    self.state.preview.resolution_use = self.window.checkBox.isChecked()

    # Check if the values are empty, if so, set them to 0.
    samples = self.window.spinBox_3.cleanText()
    self.state.preview.samples = int(samples) if samples else 0

    frame_step = self.window.spinBox_2.cleanText()
    self.state.preview.frame_step = int(frame_step) if frame_step else 0

    resolution = self.window.spinBox.cleanText()
    self.state.preview.resolution = int(resolution) if resolution else 0

    fps = self.window.spinBox_4.cleanText()
    self.state.fps = int(fps) if resolution else 0

    del self.state.addons[:]
    addons_str = self.window.lineEdit_4.text()
    for addon in addons_str.split(";"):
      self.state.addons.append(addon)
