"""Main file to open RenderRob."""
import json
import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog

import render_job
import table_utils
import ui_utils
from render_rob_state import RenderRobState

STATE = RenderRobState()


class SettingsWindow():
  """Settings dialog for RenderRob."""

  def __init__(self) -> None:
    """Open the settings dialog."""
    self.window = ui_utils.load_ui_from_file("settings.ui")
    # Load state into the settings dialog.
    self.make_settings_window_connections(self.window)

    self.window.lineEdit_3.setText(STATE.settings.blender_path)
    self.window.lineEdit_2.setText(STATE.settings.output_path)
    self.window.lineEdit.setText(STATE.settings.blender_files_path)

    self.window.checkBox_2.setCheckState(
        Qt.Checked if STATE.settings.preview.samples_use else Qt.Unchecked)
    self.window.checkBox_3.setCheckState(
        Qt.Checked if STATE.settings.preview.nth_frame_use else Qt.Unchecked)
    self.window.checkBox.setCheckState(
        Qt.Checked if STATE.settings.preview.resolution_use else Qt.Unchecked)

    self.window.spinBox_3.setValue(int(STATE.settings.preview.samples))
    self.window.spinBox_2.setValue(int(STATE.settings.preview.nth_frame))
    self.window.spinBox.setValue(int(STATE.settings.preview.resolution))

    self.window.lineEdit_4.setText(";".join(STATE.settings.addons_to_activate))

    self.window.exec()

  def make_settings_window_connections(self, window: QUiLoader) -> None:
    """Make connections for buttons in settings dialog.."""
    window.buttonBox.accepted.connect(self.save_settings_state)

  def save_settings_state(self) -> None:
    """Save the state from the settings dialog into the global state."""
    STATE.settings.blender_path = self.window.lineEdit_3.text()
    STATE.settings.output_path = self.window.lineEdit_2.text()
    STATE.settings.blender_files_path = self.window.lineEdit.text()

    STATE.settings.preview.samples_use = self.window.checkBox_2.isChecked()
    STATE.settings.preview.nth_frame_use = self.window.checkBox_3.isChecked()
    STATE.settings.preview.resolution_use = self.window.checkBox.isChecked()

    STATE.settings.preview.samples = self.window.spinBox_3.cleanText()
    STATE.settings.preview.nth_frame = self.window.spinBox_2.cleanText()
    STATE.settings.preview.resolution = self.window.spinBox.cleanText()

    STATE.settings.addons_to_activate = self.window.lineEdit_4.text()


class MainWindow():
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.window = None
    self.table = None
    self.main()

  def main(self) -> None:
    """Provide main function."""
    app = QApplication(sys.argv)
    main_window = ui_utils.load_ui_from_file("window.ui")
    self.window = main_window
    self.table = main_window.tableWidget
    table_utils.post_process_row(self.table, 0)
    self.post_process_progress_bar()
    self.make_main_window_connections()
    self.window.show()

    sys.exit(app.exec())

  def save_state(self) -> None:
    """Save the state to a JSON file."""
    STATE.render_jobs = list(render_job.jobs_from_table_widget(self.table))
    with open("state.json", "w", encoding="UTF-8") as json_file:
      json.dump(STATE.to_dict(), json_file)

  def open_file(self) -> None:
    """Open a RenderRob file."""
    # TODO(b/1234567): Change file to .rr file.
    file_name, _ = QFileDialog.getOpenFileName(
        self.window, "Open File", "", "RenderRob Files (*.json)")
    STATE.open_from_json(file_name)
    STATE.to_table(self.table)

  def make_main_window_connections(self) -> None:
    """Make connections for buttons."""
    table_utils.TABLE = self.table
    self.window.add_button.clicked.connect(table_utils.add_row_below)
    self.window.delete_button.clicked.connect(table_utils.remove_active_row)
    self.window.up_button.clicked.connect(table_utils.move_row_up)
    self.window.down_button.clicked.connect(table_utils.move_row_down)

    self.window.render_button.clicked.connect(self.start_render)
    self.window.actionOpen.triggered.connect(self.open_file)
    self.window.actionSave.triggered.connect(self.save_state)
    self.window.actionSettings.triggered.connect(SettingsWindow)

  def post_process_progress_bar(self) -> None:
    """Post-process a window after loading it from a UI file."""
    self.window.progressBar.setValue(0)

  def start_render(self) -> None:
    """Render operator called by the Render button."""""
    for i in (render_job.jobs_from_table_widget(self.table)):
      print(i.to_dict())


if __name__ == "__main__":
  MainWindow()
