"""Utility functions for table operations."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

import utils.ui_utils as ui_utils

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
    set_text_alignment(TABLE, row + 1)


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
    set_text_alignment(TABLE, row - 1)


def add_row_below() -> None:
  """Add a row below the current row."""
  current_row = TABLE.currentRow()
  TABLE.insertRow(current_row + 1)
  ui_utils.fill_row(TABLE, current_row + 1)
  set_text_alignment(TABLE, current_row + 1)


def remove_active_row() -> None:
  """Remove the currently selected row."""
  current_row = TABLE.currentRow()
  TABLE.removeRow(current_row)


def post_process_row(table: QTableWidget, row: int) -> None:
  """Post-process the table after loading it from a UI file."""
  # set_text_alignment(table, row)

  header = table.horizontalHeader()
  header.setMinimumHeight(50)
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
       ])

  # Set the file column to stretch. The other columns will be resized to fit
  # their contents. Some of the functions here might be obsolete though. Needed
  # to be checked later.
  header.setSectionResizeMode(QHeaderView.ResizeToContents)
  header.setSectionResizeMode(1, QHeaderView.Stretch)
  table.resizeColumnsToContents()
  ui_utils.fill_row(table, row)


def set_text_alignment(table: QTableWidget, row: int) -> None:
  """Set the text alignment of the table items."""
  for i in range(table.columnCount()):
    if i in ui_utils.COMBOBOX_COLUMNS or i in ui_utils.CHECKBOX_COLUMNS:
      continue
    old_item = table.item(row, i)
    if not old_item:
      text = None
    else:
      text = old_item.text()
    item = QTableWidgetItem(text)
    if not item:
      continue
    table.removeCellWidget(row, i)
    if i == 1:
      item.setTextAlignment(Qt.AlignRight)
      # TODO: Is vertical center needed?
      # item.setTextAlignment(Qt.AlignRight)
    else:
      item.setTextAlignment(Qt.AlignCenter)
    table.setItem(row, i, item)
