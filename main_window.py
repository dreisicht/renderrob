"""Main file to open RenderRob."""
import json
import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog

import utils.table_utils as table_utils
import utils.ui_utils as ui_utils
import state_saver

STATESAVER = state_saver.StateSaver()


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
    main_window = ui_utils.load_ui_from_file("ui/window.ui")
    self.window = main_window
    self.table = main_window.tableWidget
    table_utils.post_process_row(self.table, 0)
    self.post_process_progress_bar()
    self.make_main_window_connections()
    self.window.show()

    sys.exit(app.exec())

  def save_state(self) -> None:
    """Save the state to a JSON file."""
    STATESAVER.table_to_state(self.table)
    with open("state.pb", "wb") as protobuf:
      protobuf.write(STATESAVER.state.SerializeToString(protobuf))

  def open_file(self) -> None:
    """Open a RenderRob file."""
    # TODO(b/1234567): Change file to .rr file.
    file_name, _ = QFileDialog.getOpenFileName(
        self.window, "Open File", "", "RenderRob Files (*.pb)")
    with open(file_name, "rb") as pb_file:
      pb_str = pb_file.read()
    STATESAVER.state.ParseFromString(pb_str)
    STATESAVER.state_to_table(self.table)

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
    print(STATESAVER.state.__dict__)


if __name__ == "__main__":
  MainWindow()
