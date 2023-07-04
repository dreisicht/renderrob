"""Utility functions for table operations."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget

import ui_utils

TABLE = None
# Note: This variable is required because when using clicked.connect() the argument is
# only the function. Therefore arguments to the function cannot be passed.


def move_row_down() -> None:
  """Move the currently selected row down."""
  row = TABLE.currentRow()
  column = TABLE.currentColumn()
  if row < TABLE.rowCount() - 1:
    combobox_values = list(ui_utils.get_combobox_indexes(TABLE, row))
    checkbox_values = list(ui_utils.get_checkbox_values(TABLE, row))
    TABLE.insertRow(row + 2)
    for i in range(TABLE.columnCount()):
      TABLE.setItem(row + 2, i, TABLE.takeItem(row, i))
      TABLE.setCurrentCell(row + 2, column)
    TABLE.removeRow(row)
    ui_utils.fill_row(TABLE, row + 1)
    ui_utils.set_combobox_indexes(TABLE, row + 1, combobox_values)
    ui_utils.set_checkbox_values(TABLE, row + 1, checkbox_values)


def move_row_up() -> None:
  """Move the currently selected row up."""
  row = TABLE.currentRow()
  column = TABLE.currentColumn()
  if row > 0:
    combobox_values = list(ui_utils.get_combobox_indexes(TABLE, row))
    checkbox_values = list(ui_utils.get_checkbox_values(TABLE, row))
    TABLE.insertRow(row - 1)
    for i in range(TABLE.columnCount()):
      TABLE.setItem(row - 1, i, TABLE.takeItem(row + 1, i))
      TABLE.setCurrentCell(row - 1, column)
    TABLE.removeRow(row + 1)
    ui_utils.fill_row(TABLE, row - 1)
    ui_utils.set_combobox_indexes(TABLE, row - 1, combobox_values)
    ui_utils.set_checkbox_values(TABLE, row - 1, checkbox_values)


def add_row_below() -> None:
  """Add a row below the current row."""
  current_row = TABLE.currentRow()
  TABLE.insertRow(current_row + 1)
  ui_utils.fill_row(TABLE, current_row + 1)


def remove_active_row() -> None:
  """Remove the currently selected row."""
  current_row = TABLE.currentRow()
  TABLE.removeRow(current_row)


def post_process_row(table: QTableWidget, row: int) -> None:
  """Post-process the table after loading it from a UI file."""
  table.horizontalHeader().setDefaultAlignment(
      Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap))
  table.horizontalHeader().setMinimumHeight(50)
  table.setHorizontalHeaderLabels(
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
  table.resizeColumnsToContents()
  ui_utils.fill_row(table, row)
