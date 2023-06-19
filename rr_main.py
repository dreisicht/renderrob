"""Main file to open RenderRob."""
import sys

from PySide6.QtCore import QCoreApplication, QFile, QIODevice, QProcess, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

import render_job
import ui_utils


class MainWindow():
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    self.window = None
    self.table = None
    self.load_ui_from_file("rr.ui")

  def load_ui_from_file(self, ui_file_name: str) -> None:
    """Load a UI file from the given path and return the widget."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
      print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
      sys.exit(-1)
    loader = QUiLoader()
    self.window = loader.load(ui_file)
    self.table = self.window.tableWidget

    ui_file.close()
    if not self.window:
      print(loader.errorString())
      sys.exit(-1)

    self.post_process_row(0)
    self.post_process_progress_bar()
    self.make_connections()
    self.window.show()

    sys.exit(app.exec())

  def move_row_down(self) -> None:
    """Move the currently selected row down."""
    row = self.table.currentRow()
    column = self.table.currentColumn()
    if row < self.table.rowCount() - 1:
      combobox_values = list(ui_utils.get_combobox_indexes(self.table, row))
      checkbox_values = list(ui_utils.get_checkbox_values(self.table, row))
      self.table.insertRow(row + 2)
      for i in range(self.table.columnCount()):
        self.table.setItem(row + 2, i, self.table.takeItem(row, i))
        self.table.setCurrentCell(row + 2, column)
      self.table.removeRow(row)
      ui_utils.fill_row(self.table, row + 1)
      ui_utils.set_combobox_indexes(self.table, row + 1, combobox_values)
      ui_utils.set_checkbox_values(self.table, row + 1, checkbox_values)

  def move_row_up(self) -> None:
    """Move the currently selected row up."""
    row = self.table.currentRow()
    column = self.table.currentColumn()
    if row > 0:
      combobox_values = list(ui_utils.get_combobox_indexes(self.table, row))
      checkbox_values = list(ui_utils.get_checkbox_values(self.table, row))
      self.table.insertRow(row - 1)
      for i in range(self.table.columnCount()):
        self.table.setItem(row - 1, i, self.table.takeItem(row + 1, i))
        self.table.setCurrentCell(row - 1, column)
      self.table.removeRow(row + 1)
      ui_utils.fill_row(self.table, row - 1)
      ui_utils.set_combobox_indexes(self.table, row - 1, combobox_values)
      ui_utils.set_checkbox_values(self.table, row - 1, checkbox_values)

  def add_row_below(self) -> None:
    """Add a row below the current row."""
    current_row = self.table.currentRow()
    self.table.insertRow(current_row + 1)
    ui_utils.fill_row(self.table, current_row + 1)

  def remove_active_row(self) -> None:
    """Remove the currently selected row."""
    current_row = self.table.currentRow()
    self.table.removeRow(current_row)

  def make_connections(self) -> None:
    """Make connections for buttons."""
    self.window.add_button.clicked.connect(self.add_row_below)
    self.window.delete_button.clicked.connect(self.remove_active_row)
    self.window.up_button.clicked.connect(self.move_row_up)
    self.window.down_button.clicked.connect(self.move_row_down)
    self.window.render_button.clicked.connect(self.render_jobs)

  def post_process_row(self, row: int) -> None:
    """Post-process the table after loading it from a UI file."""
    self.table.horizontalHeader().setDefaultAlignment(
        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap))
    self.table.horizontalHeader().setMinimumHeight(50)
    self.table.setHorizontalHeaderLabels(
        ["Active",
         "File",
         "Camera",
         "Start",
         "End",
         "X\nRes",
         "Y\nRes",
         "Samples",
         "File\nFormat",
         "Engine",
         "Device",
         "Motion\nBlur",
         "New\nVersion",
         "High\nQuality",
         "Animation\nDenoise",
         "Denoise",
         "Scene",
         "View\nLayer",
         "Comments",
         "View\nOutput"
         ])
    self.table.resizeColumnsToContents()
    ui_utils.fill_row(self.table, row)

  def post_process_progress_bar(self) -> None:
    """Post-process a window after loading it from a UI file."""
    self.window.progressBar.setValue(0)

  def render_jobs(self) -> None:
    """Render operator called by the Render button."""""
    for i in (render_job.render_jobs_from_table_widget(self.table)):
      print(vars(i))


if __name__ == "__main__":
  MainWindow()
