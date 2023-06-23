"""Utility functions for table operations."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget

import ui_utils


def move_row_down(table: QTableWidget) -> None:
  """Move the currently selected row down."""
  row = table.currentRow()
  column = table.currentColumn()
  if row < table.rowCount() - 1:
    combobox_values = list(ui_utils.get_combobox_indexes(table, row))
    checkbox_values = list(ui_utils.get_checkbox_values(table, row))
    table.insertRow(row + 2)
    for i in range(table.columnCount()):
      table.setItem(row + 2, i, table.takeItem(row, i))
      table.setCurrentCell(row + 2, column)
    table.removeRow(row)
    ui_utils.fill_row(table, row + 1)
    ui_utils.set_combobox_indexes(table, row + 1, combobox_values)
    ui_utils.set_checkbox_values(table, row + 1, checkbox_values)


def move_row_up(table: QTableWidget) -> None:
  """Move the currently selected row up."""
  row = table.currentRow()
  column = table.currentColumn()
  if row > 0:
    combobox_values = list(ui_utils.get_combobox_indexes(table, row))
    checkbox_values = list(ui_utils.get_checkbox_values(table, row))
    table.insertRow(row - 1)
    for i in range(table.columnCount()):
      table.setItem(row - 1, i, table.takeItem(row + 1, i))
      table.setCurrentCell(row - 1, column)
    table.removeRow(row + 1)
    ui_utils.fill_row(table, row - 1)
    ui_utils.set_combobox_indexes(table, row - 1, combobox_values)
    ui_utils.set_checkbox_values(table, row - 1, checkbox_values)


def add_row_below(table: QTableWidget) -> None:
  """Add a row below the current row."""
  current_row = table.currentRow()
  table.insertRow(current_row + 1)
  ui_utils.fill_row(table, current_row + 1)


def remove_active_row(table: QTableWidget) -> None:
  """Remove the currently selected row."""
  current_row = table.currentRow()
  table.removeRow(current_row)


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
