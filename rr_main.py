"""Main file to open RenderRob."""
import sys
import json

from PySide6.QtCore import QCoreApplication, QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog

import render_job
from render_rob_state import RenderRobState
import table_utils


class MainWindow():
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.window = None
    self.table = None
    self.state = RenderRobState()
    self.main()

  def main(self) -> None:
    """Provide main function."""
    app = QApplication(sys.argv)
    window = self.load_ui_from_file("window.ui")
    self.window = window
    self.table = window.tableWidget
    table_utils.post_process_row(self.table, 0)
    self.post_process_progress_bar()
    self.make_main_window_connections()
    self.window.show()

    sys.exit(app.exec())

  def on_accepted(self) -> None:
    """Handle the accepted signal from the settings dialog."""
    print("Accepted")

  def make_settings_connections(self, window) -> None:
    """Make connections for the settings dialog."""
    window.buttonBox.accepted.connect(self.on_accepted)

  def open_settings_dialog(self) -> None:
    """Open the settings dialog."""
    window = self.load_ui_from_file("settings.ui")
    window.exec()

  def save_state(self) -> None:
    """Save the state to a JSON file."""
    self.state.render_jobs = list(render_job.jobs_from_table_widget(self.table))
    with open("state.json", "w", encoding="UTF-8") as json_file:
      json.dump(self.state.to_dict(), json_file)

  def open_file(self) -> None:
    """Open a RenderRob file."""
    # TODO(b/1234567): Change file to .rr file.
    file_name, _ = QFileDialog.getOpenFileName(
        self.window, "Open File", "", "RenderRob Files (*.json)")
    self.state.open_from_json(file_name)
    self.state.to_table(self.table)

  def load_ui_from_file(self, ui_file_name: str) -> QUiLoader:
    """Load a UI file from the given path and return the widget."""
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
      print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
      sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)

    ui_file.close()
    if not window:
      print(loader.errorString())
      sys.exit(-1)
    return window

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
    self.window.actionSettings.triggered.connect(self.open_settings_dialog)

  def post_process_progress_bar(self) -> None:
    """Post-process a window after loading it from a UI file."""
    self.window.progressBar.setValue(0)

  def start_render(self) -> None:
    """Render operator called by the Render button."""""
    for i in (render_job.jobs_from_table_widget(self.table)):
      print(i.to_dict())


if __name__ == "__main__":
  MainWindow()
