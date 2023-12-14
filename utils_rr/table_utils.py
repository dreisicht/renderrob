"""Utility functions for table operations."""
from typing import Any, Optional

from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHeaderView, QStyledItemDelegate, QTableWidget,
                               QTableWidgetItem, QWidget)
from utils_rr import ui_utils, path_utils

COLORS = {
    "red": 0x980030,
    "yellow": 0xffd966,
    "green": 0x9fd3b6,
    "blue": 0x57a3b4,
    "blue_grey_lighter": 0x6397bd,
    "blue_grey": 0x4f7997,
    "blue_grey_darker": 0x345064,
    "grey_light": 0xebebeb,
    "grey_inactive": 0xf8f8f8,
    "grey_neutral": 0x999999,
    "black_light": 0x22282b,
    "black_dark": 0x242a2d,
    "white": 0xffffff,
}


def fix_active_row_path(item: QTableWidgetItem, blend_folder: str) -> None:
  """Fix the path of the currently selected row."""
  path = item.text()
  path = path_utils.normalize_drive_letter(path)
  path = path.replace('"', "").replace("\\", "/")
  if blend_folder:
    path = path_utils.get_rel_blend_path(path, blend_folder)
  item.setText(path)


def make_editable(table_widget: QTableWidget) -> None:
  """Undo the make QTableWidget only selectable."""
  class EditableDelegate(QStyledItemDelegate):
    """Allow editing of QTableWidget."""

    def createEditor(self, parent, option, index):  # pylint: disable=invalid-name
      """Allow editing by returning the default editor"""
      return QStyledItemDelegate.createEditor(self, parent, option, index)
  delegate = EditableDelegate()
  table_widget.setItemDelegate(delegate)
  for row in range(table_widget.rowCount()):
    for col in ui_utils.COMBOBOX_COLUMNS:
      widget = table_widget.cellWidget(row, col)
      if widget and isinstance(widget, QComboBox):
        widget.setDisabled(False)

    for col in ui_utils.CHECKBOX_COLUMNS:
      widget = table_widget.cellWidget(row, col)
      checkbox_item = widget.findChild(QCheckBox)
      if widget and isinstance(widget, QWidget):
        checkbox_item.setDisabled(False)


def make_read_only_selectable(table_widget: QTableWidget) -> None:
  """Make QTableWidget only selectable."""
  #  #10 Set the render button to disabled.
  class ReadOnlyDelegate(QStyledItemDelegate):
    """Prevent editing of QTableWidget."""

    def createEditor(self, parent, option, index):  # pylint: disable=invalid-name
      """Prevent editing of QTableWidget by returning None."""
      del parent, option, index
  delegate = ReadOnlyDelegate()
  table_widget.setItemDelegate(delegate)
  for row in range(table_widget.rowCount()):
    for col in ui_utils.COMBOBOX_COLUMNS:
      combobox_item = table_widget.cellWidget(row, col)
      if combobox_item and isinstance(combobox_item, QComboBox):
        combobox_item.setEditable(False)
        combobox_item.setDisabled(True)

    for col in ui_utils.CHECKBOX_COLUMNS:
      widget = table_widget.cellWidget(row, col)
      checkbox_item = widget.findChild(QCheckBox)
      checked = checkbox_item.isChecked()
      if widget and isinstance(widget, QWidget):
        # checkbox_item.setCheckable(False)
        checkbox_item.setDisabled(True)
        checkbox_item.setChecked(checked)


# @operator
def move_row_down(table_widget: QTableWidget, before_callback_function: callable,
                  after_callback_function: callable) -> None:
  """Move the currently selected row down."""
  table_widget.blockSignals(True)
  before_callback_function()

  row = table_widget.currentRow()
  column = table_widget.currentColumn()
  if row < table_widget.rowCount() - 1:
    combobox_values = list(ui_utils.get_combobox_indexes(table_widget, row))
    checkbox_values = list(ui_utils.get_checkbox_values(table_widget, row))
    table_widget.insertRow(row + 2)
    for i in range(table_widget.columnCount()):
      table_widget.setItem(row + 2, i, table_widget.takeItem(row, i))
      table_widget.setCurrentCell(row + 2, column)
    table_widget.removeRow(row)
    ui_utils.fill_row(table_widget, row + 1)
    ui_utils.set_combobox_indexes(table_widget, row + 1, combobox_values)
    ui_utils.set_checkbox_values(table_widget, row + 1, checkbox_values)
    set_text_alignment(table_widget, row + 1)

  after_callback_function()
  table_widget.blockSignals(False)


# @operator
def move_row_up(table_widget: QTableWidget, before_callback_function: callable,
                after_callback_function: callable) -> None:
  """Move the currently selected row up."""
  table_widget.blockSignals(True)
  before_callback_function()

  row = table_widget.currentRow()
  column = table_widget.currentColumn()
  if row > 0:
    combobox_values = list(ui_utils.get_combobox_indexes(table_widget, row))
    checkbox_values = list(ui_utils.get_checkbox_values(table_widget, row))
    table_widget.insertRow(row - 1)
    for i in range(table_widget.columnCount()):
      table_widget.setItem(row - 1, i, table_widget.takeItem(row + 1, i))
      table_widget.setCurrentCell(row - 1, column)
    table_widget.removeRow(row + 1)
    ui_utils.fill_row(table_widget, row - 1)
    ui_utils.set_combobox_indexes(table_widget, row - 1, combobox_values)
    ui_utils.set_checkbox_values(table_widget, row - 1, checkbox_values)
    set_text_alignment(table_widget, row - 1)

  after_callback_function()
  table_widget.blockSignals(False)


# @operator
def duplicate_row(table_widget: QTableWidget, state_saver: Any,
                  before_callback_function: callable, after_callback_function: callable) -> None:
  """Duplicate the currently selected row."""
  table_widget.blockSignals(True)
  before_callback_function()

  state_saver.table_to_state(table_widget)
  current_row = table_widget.currentRow()
  state_saver.state.render_jobs.insert(
      current_row + 1, state_saver.state.render_jobs[current_row])
  state_saver.state_to_table(table_widget)

  after_callback_function()
  table_widget.blockSignals(False)


# @operator
def add_row_below(table_widget: QTableWidget,
                  before_callback_function: Optional[callable] = None,
                  after_callback_function: Optional[callable] = None) -> None:
  """Add a row below the current row."""
  table_widget.blockSignals(True)
  if before_callback_function:
    before_callback_function()

  current_row = table_widget.currentRow() + 1
  table_widget.insertRow(current_row)
  ui_utils.fill_row(table_widget, current_row)
  set_text_alignment(table_widget, current_row)

  if after_callback_function:
    after_callback_function()
  table_widget.blockSignals(False)


# @operator
def remove_active_row(table_widget: QTableWidget, before_callback_function: callable,
                      after_callback_function: callable) -> None:
  """Remove the currently selected row."""
  table_widget.blockSignals(True)
  before_callback_function()

  current_row = table_widget.currentRow()
  if current_row == -1:
    current_row = table_widget.rowCount() - 1
  table_widget.removeRow(current_row)

  after_callback_function()
  table_widget.blockSignals(False)


# @operator
def add_file_below(table_widget: QTableWidget, path: str) -> None:
  """Add a file below the current row."""
  table_widget.blockSignals(True)
  id_row = table_widget.rowCount()
  table_widget.insertRow(id_row)
  ui_utils.fill_row(table_widget, id_row)
  set_text_alignment(table_widget, id_row)
  table_widget.setItem(id_row, 1, QTableWidgetItem(path))
  table_widget.blockSignals(False)


def post_process_row(table_widget: QTableWidget, row: int) -> None:
  """Post-process the table after loading it from a UI file."""

  header = table_widget.horizontalHeader()
  header.setMinimumHeight(50)
  table_widget.setHorizontalHeaderLabels(
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
       "Continue\nJob",
       "Final\nMode",
       "Denoise",
       "Scene",
       "View\nLayers",
       "Comments",
       ])

  # Set the file column to stretch. The other columns will be resized to fit
  # their contents. Some of the functions here might be obsolete though. Needed
  # to be checked later.
  header.setSectionResizeMode(QHeaderView.ResizeToContents)
  header.setSectionResizeMode(1, QHeaderView.Stretch)
  # header.setSectionResizeMode(17, QHeaderView.Fixed)
  table_widget.resizeColumnsToContents()
  ui_utils.fill_row(table_widget, row)


def set_text_alignment(table_widget: QTableWidget, row: int) -> None:
  """Set the text alignment of the table items."""
  for i in range(table_widget.columnCount()):
    if i in ui_utils.COMBOBOX_COLUMNS or i in ui_utils.CHECKBOX_COLUMNS:
      continue
    old_item = table_widget.item(row, i)
    if old_item:
      text = old_item.text()
    else:
      text = ""
    item = QTableWidgetItem(text)
    if not item:
      continue
    table_widget.removeCellWidget(row, i)
    if i == 1:
      item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    else:
      item.setTextAlignment(Qt.AlignCenter)
    table_widget.setItem(row, i, item)


def color_row_background(table_widget: QTableWidget, row_index: int, base_color: QColor) -> None:
  """Color the background of a row."""

  # Taking the background color of the camera tableitem as reference.
  previous_color = table_widget.item(row_index, 2).background()

  color = base_color
  if previous_color == QColor(COLORS["red"]):
    color = QColor(COLORS["red"])
  elif previous_color == QColor(COLORS["yellow"]):
    if base_color == QColor(COLORS["green"]):
      color = QColor(COLORS["yellow"])

  for column_index in range(table_widget.columnCount()):
    item = table_widget.item(row_index, column_index)

    if column_index in ui_utils.CHECKBOX_COLUMNS:
      ui_utils.set_checkbox_background_color(
          table_widget, row_index, column_index, color)

    # Check if the value in the numbers columns is valid.
    if item and item.text() and (
            column_index in ui_utils.NUMBER_COLUMNS and not item.text().isnumeric()):
      item.setBackground(QColor(COLORS["red"]))
    elif item:
      item.setBackground(color)
