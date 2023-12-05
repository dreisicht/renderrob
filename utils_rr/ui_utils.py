"""Util functions for helping build the render rob UI."""
import sys
from contextlib import closing
from typing import Any, List, Optional

from PySide6.QtCore import QFile, QMetaObject, Qt
from PySide6.QtGui import QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QTableWidget, QWidget

TEXT_COLUMNS = [1, 2, 15, 16, 17]
NUMBER_COLUMNS = [3, 4, 5, 6, 7]
COMBOBOX_COLUMNS = [8, 9, 10]
CHECKBOX_COLUMNS = [0, 11, 12, 13, 14]
FILE_FORMATS_COMMAND = ["OPEN_EXR", "OPEN_EXR_MULTILAYER", "JPEG", "PNG", "TIFF", "FFMPEG"]
FILE_FORMATS_UI = ["exr single", "exr multi", "jpeg", "png", "tiff", "ffmpeg"]
FILE_FORMATS_ACTUAL = ["exr", "exr", "jpg", "png", "tiff", "ffmpeg"]
FILEMFORMAT_MAPPING = {
    "png": "png",
    "jpeg": "jpeg",
    "tiff": "tiff",
    "open_exr_multilayer": "exr_mutli",
    "open_exr": "exr_single",
    "ffmpeg": "ffmpeg"
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
TABLE_CHANGED_FUNCTION = None


def load_ui_from_file(ui_file_name: str, custom_widgets: Optional[List[Any]] = None) -> QUiLoader:
  """Load a UI file from the given path and return the widget."""
  ui_loader = QUiLoader()
  if custom_widgets:
    for custom_widget in custom_widgets:
      ui_loader.registerCustomWidget(custom_widget)
  ui_file = QFile(ui_file_name)

  with closing(ui_file) as qt_file:
    if qt_file.open(QFile.ReadOnly):
      window = ui_loader.load(qt_file)
    else:
      print('Failed to read UI')

  if not window:
    print(ui_loader.errorString())
    sys.exit(-1)
  QMetaObject.connectSlotsByName(window)
  return window


def get_combobox_indexes(table: QTableWidget, row: int) -> list:
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


def get_checkbox_values(table: QTableWidget, row: int) -> list:
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


def set_combobox_background_color(table: QTableWidget, row: int, color: QColor) -> None:
  """Set color of comboboxes."""
  for i in COMBOBOX_COLUMNS:
    widget = table.cellWidget(row, i)
    if widget:
      widget.setStyleSheet(
          f"QComboBox:drop-down {{background-color: {color.name()};}}")


def set_checkbox_background_color(table: QTableWidget, row: int, col: int, color: QColor) -> None:
  """Set color of checkboxes."""
  widget = table.cellWidget(row, col)
  if widget:
    widget.setStyleSheet(f"background-color: {color.name()};")


def add_checkbox(table: QTableWidget, row: int, col: int, checked=False):
  """Add a checkbox to the given table at the given row and column."""
  widget = QWidget()
  check_box = QCheckBox()
  # Warning: Setting the size way bigger here, so that the click area is bigger. If other styles
  # are used, this might need to be adjusted. See in renderrob.py: self.app.setStye("Breeze")
  check_box.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
  layout = QHBoxLayout(widget)
  layout.addWidget(check_box)
  layout.setAlignment(Qt.AlignCenter)
  layout.setContentsMargins(0, 0, 0, 0)
  widget.setLayout(layout)
  check_box.setCheckState(Qt.Checked if checked else Qt.Unchecked)
  # Refactor: Hook up checkboxes with table_changed function.
  check_box.clicked.connect(TABLE_CHANGED_FUNCTION)
  table.setCellWidget(row, col, widget)


def add_dropdown(table: QTableWidget, row: int, col: int, items):
  """Add a dropdown to the given table at the given row and column."""
  dropdown = QComboBox()
  dropdown.addItems(items)
  dropdown.currentIndexChanged.connect(TABLE_CHANGED_FUNCTION)
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
