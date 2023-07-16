"""Util functions for helping build the render rob UI."""

import sys

from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QTableWidget,
                               QWidget, QPushButton)

COMBOBOX_COLUMNS = [8, 9, 10]
CHECKBOX_COLUMNS = [0, 11, 12, 13, 14, 15]
FILE_FORMATS = ["png", "tiff", "exr", "jpg"]
RENDER_ENGINES = ["cycles", "eevee"]
DEVICES = ["gpu", "cpu"]


def load_ui_from_file(ui_file_name: str) -> QUiLoader:
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


def get_combobox_indexes(table: QTableWidget, row: int) -> list:
  """Get all values of combo boxes in a row."""
  for i in COMBOBOX_COLUMNS:
    yield table.cellWidget(row, i).currentIndex()


def set_combobox_indexes(table: QTableWidget, row: int, values: list[int]) -> None:
  """Set all values of combo boxes in a row."""
  for j, i in enumerate(COMBOBOX_COLUMNS):
    table.cellWidget(row, i).setCurrentIndex(values[j])


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
    checkbox_item.setChecked(values[j])


def add_checkbox(table: QTableWidget, row: int, col: int, checked=False):
  """Add a checkbox to the given table at the given row and column."""
  widget = QWidget()
  check_box = QCheckBox()
  layout = QHBoxLayout(widget)
  layout.addWidget(check_box)
  layout.setAlignment(Qt.AlignCenter)
  layout.setContentsMargins(0, 0, 0, 0)
  widget.setLayout(layout)
  check_box.setCheckState(Qt.Checked if checked else Qt.Unchecked)
  table.setCellWidget(row, col, widget)


def add_dropdown(table: QTableWidget, row: int, col: int, items):
  """Add a dropdown to the given table at the given row and column."""
  dropdown = QComboBox()
  dropdown.addItems(items)
  table.setCellWidget(row, col, dropdown)


def fill_row(table: QTableWidget, row: int) -> None:
  """Fill the table with widgets values."""
  add_checkbox(table, row, 0, checked=True)
  add_dropdown(table, row, 8, FILE_FORMATS)
  add_dropdown(table, row, 9, RENDER_ENGINES)
  add_dropdown(table, row, 10, DEVICES)
  add_checkbox(table, row, 11, checked=False)
  add_checkbox(table, row, 12, checked=False)
  add_checkbox(table, row, 13, checked=False)
  add_checkbox(table, row, 14, checked=False)
  add_checkbox(table, row, 15, checked=False)
