"""Util functions for helping build the render rob UI."""

import sys
from collections.abc import Callable, Generator
from contextlib import closing
from importlib import resources
from pathlib import Path
from string import Template
from typing import Any

from PySide6.QtCore import QDir, QFile, QMetaObject, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
  QCheckBox,
  QComboBox,
  QHBoxLayout,
  QTableWidget,
  QTableWidgetItem,
  QWidget,
)

import ui
from utils_common import print_utils

TEXT_COLUMNS = [1, 2, 15, 16, 17]
NUMBER_COLUMNS = [3, 4, 5, 6, 7]
COMBOBOX_COLUMNS = [8, 9, 10]
CHECKBOX_COLUMNS = [0, 11, 12, 13, 14]
FILE_FORMATS_COMMAND = ["OPEN_EXR", "OPEN_EXR_MULTILAYER", "JPEG", "PNG", "TIFF"]
FILE_FORMATS_UI = ["exr single", "exr multi", "jpeg", "png", "tiff"]
FILE_FORMATS_ACTUAL = ["exr", "exr", "jpg", "png", "tiff"]
FILEMFORMAT_MAPPING = {
  "png": "png",
  "jpeg": "jpeg",
  "tiff": "tiff",
  "open_exr_multilayer": "exr_multi",
  "open_exr": "exr_single",
}

RENDER_ENGINES = ["cycles", "eevee"]
DEVICES = ["gpu", "cpu"]
PLACEHOLDER_TEXT = {
  1: "File",
  2: "Camera",
  3: "Start",
  4: "End",
  5: "X Res",
  6: "Y Res",
  7: "Samples",
  15: "Scene",
  16: "View Layers",
  17: "Comments",
}
# Set by main.py once the main window exists, so the table widgets can report their edits.
TABLE_CHANGED_FUNCTION: Callable[..., None] | None = None


STYLESHEET_FILE_NAME = "style.qss"


def resolve_ui_file(file_name: str) -> Path:
  """Find a file shipped in the ui package.

  Where it lives depends on how Render Rob was started: from the repository, from the working
  directory of a frozen build, or from inside the installed package.
  """
  if Path(file_name).exists():
    return Path(file_name)
  if (Path("ui") / file_name).exists():
    return Path("ui") / file_name
  return Path(str(resources.files(ui) / file_name))


def load_stylesheet(colors: dict[str, int]) -> str:
  """Build the application stylesheet for the given palette.

  The .qss file is written with $placeholders so that the same rules serve the light and the dark
  theme; see utils_rr/table_utils.py for the palettes.

  Styling is cosmetic, so a bundle that is missing the file still starts, just unstyled.
  """
  stylesheet_path = resolve_ui_file(STYLESHEET_FILE_NAME)
  if not stylesheet_path.is_file():
    print_utils.print_warning(f"I couldn't find my stylesheet at {stylesheet_path}.")
    return ""
  substitutions = {name: f"#{value:06x}" for name, value in colors.items()}
  # Qt needs forward slashes in url() even on Windows.
  substitutions["icons_dir"] = (stylesheet_path.parent / "icons").resolve().as_posix()
  return Template(stylesheet_path.read_text(encoding="utf-8")).substitute(substitutions)


def load_ui_from_file(ui_file_name: str, custom_widgets: list[Any] | None = None) -> QWidget:
  """Load a UI file from the given path and return the widget."""
  ui_loader = QUiLoader()

  ui_file_path = resolve_ui_file(ui_file_name)

  qt_q_dir = QDir(ui_file_path.parent)
  ui_loader.setWorkingDirectory(qt_q_dir)

  if custom_widgets:
    for custom_widget in custom_widgets:
      ui_loader.registerCustomWidget(custom_widget)

  ui_file = QFile(str(ui_file_path))

  window = None
  with closing(ui_file) as qt_file:
    if qt_file.open(QFile.ReadOnly):
      window = ui_loader.load(qt_file)
    else:
      print_utils.print_error_no_exit("Failed to read UI.")

  if not window:
    print_utils.print_error_no_exit(ui_loader.errorString())
    sys.exit(-1)
  QMetaObject.connectSlotsByName(window)
  return window


def get_combobox_indexes(table: QTableWidget, row: int) -> Generator:
  """Get all values of combo boxes in a row."""
  for i in COMBOBOX_COLUMNS:
    yield table.cellWidget(row, i).currentIndex()


def set_combobox_indexes(table: QTableWidget, row: int, values: list[int]) -> None:
  """Set all values of combo boxes in a row."""
  for j, i in enumerate(COMBOBOX_COLUMNS):
    widget = table.cellWidget(row, i)
    widget.blockSignals(True)
    widget.setCurrentIndex(values[j])
    widget.blockSignals(False)


def get_checkbox_values(table: QTableWidget, row: int) -> Generator:
  """Get all values of checkboxes in a row."""
  for i in CHECKBOX_COLUMNS:
    widget = table.cellWidget(row, i)
    checkbox_item = widget.findChild(QCheckBox)
    yield checkbox_item.isChecked()


def set_checkbox_values(table: QTableWidget, row: int, values: list[bool]) -> None:
  """Set all values of checkboxes in a row."""
  for j, i in enumerate(CHECKBOX_COLUMNS):
    widget = table.cellWidget(row, i)
    checkbox_item = widget.findChild(QCheckBox)
    checkbox_item.blockSignals(True)
    checkbox_item.setChecked(values[j])
    checkbox_item.blockSignals(False)


def add_background_item(table: QTableWidget, row: int, col: int) -> None:
  """Put an empty, inert item behind a cell that holds a widget.

  A cell widget covers the view's own background, so a cell that only contains a checkbox or a
  dropdown would stay uncolored while the rest of its row takes on the job's status color. The
  item is never read back - state_saver reads those columns via cellWidget - it exists purely so
  that color_row_background has something to paint.
  """
  item = QTableWidgetItem()
  item.setFlags(Qt.ItemIsEnabled)
  table.setItem(row, col, item)


def add_checkbox(table: QTableWidget, row: int, col: int, *, checked: bool = False) -> None:
  """Add a checkbox to the given table at the given row and column."""
  widget = QWidget()
  # The cell widget must not paint its own background, or it hides the row color.
  widget.setAttribute(Qt.WA_TranslucentBackground)
  check_box = QCheckBox()
  layout = QHBoxLayout(widget)
  layout.addWidget(check_box)
  layout.setAlignment(Qt.AlignCenter)
  layout.setContentsMargins(0, 0, 0, 0)
  widget.setLayout(layout)
  check_box.setCheckState(Qt.Checked if checked else Qt.Unchecked)
  # Refactor: Hook up checkboxes with table_changed function.
  check_box.clicked.connect(TABLE_CHANGED_FUNCTION)
  add_background_item(table, row, col)
  table.setCellWidget(row, col, widget)


def add_dropdown(table: QTableWidget, row: int, col: int, items: list[str]) -> None:
  """Add a dropdown to the given table at the given row and column."""
  dropdown = QComboBox()
  dropdown.addItems(items)
  dropdown.currentIndexChanged.connect(TABLE_CHANGED_FUNCTION)
  add_background_item(table, row, col)
  table.setCellWidget(row, col, dropdown)


def fill_row(table: QTableWidget, row: int) -> None:
  """Fill the table with widgets values."""
  add_checkbox(table, row, 0, checked=True)
  add_dropdown(table, row, 8, FILE_FORMATS_UI)
  add_dropdown(table, row, 9, RENDER_ENGINES)
  add_dropdown(table, row, 10, DEVICES)
  add_checkbox(table, row, 11, checked=False)
  add_checkbox(table, row, 12, checked=False)
  add_checkbox(table, row, 13, checked=False)
  add_checkbox(table, row, 14, checked=False)
