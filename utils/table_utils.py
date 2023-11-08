"""Utility functions for table operations."""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHeaderView, QStyledItemDelegate, QTableWidget,
                               QTableWidgetItem, QWidget)

from utils import ui_utils

COLORS = {
    "red": 0x980030,
    "yellow": 0xffd966,
    "green": 0x9fd3b6,
    "blue": 0x57a3b4,
    "blue_grey_lighter": 0x6397bd,
    "blue_grey": 0x4f7997,
    "blue_grey_darker": 0x345064,
    "grey_light": 0xebebeb,
    "grey_neutral": 0x999999,
    "black_light": 0x22282b,
    "black_dark": 0x242a2d
}


def normalize_drive_letter(path: str) -> str:
  """Normalize the drive letter to upper case."""
  if len(path) < 2:
    return path
  path = os.path.normpath(path).replace("\\", "/")
  if path[1] == ":":
    return path[0].upper() + path[1:]
  return path


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


def move_row_down(table_widget: QTableWidget) -> None:
  """Move the currently selected row down."""
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


def move_row_up(table_widget: QTableWidget) -> None:
  """Move the currently selected row up."""
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


def add_file_below(table_widget: QTableWidget, path: str) -> None:
  """Add a file below the current row."""
  table_widget.blockSignals(True)
  id_row = table_widget.rowCount()
  table_widget.insertRow(id_row)
  ui_utils.fill_row(table_widget, id_row)
  set_text_alignment(table_widget, id_row)
  table_widget.setItem(id_row, 1, QTableWidgetItem(path))
  # fix_active_row_path(table_widget.item(id_row, 1))
  table_widget.blockSignals(False)


def post_process_row(table_widget: QTableWidget, row: int) -> None:
  """Post-process the table after loading it from a UI file."""
  # set_text_alignment(table, row)

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
       "High\nQuality",
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
  table_widget.resizeColumnsToContents()
  ui_utils.fill_row(table_widget, row)


def get_blend_files_rel_path(blend_folder: str, path: str) -> str:
  """Get the blender files path."""
  if os.path.basename(path) == path:
    return path
  common = os.path.commonpath([blend_folder, path])
  return os.path.relpath(path, common)


def fix_active_row_path(item: QTableWidgetItem, blend_folder: str) -> None:
  """Fix the path of the currently selected row."""
  path = item.text()
  path = normalize_drive_letter(path)
  path = path.replace('"', "").replace("\\", "/")
  if blend_folder:
    path = get_blend_files_rel_path(blend_folder, path)
  item.setText(path)


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


def color_row_background(table_widget: QTableWidget, row_index: int, color: QColor) -> None:
  """Color the background of a row."""
  #  #3 Add coloring for upfront warnings (double jobs, animation denoising,
  # but exr selected, high quality and animation but no animation denoising,
  # single frame rendering but animation denoising,
  # single frame rendering in high quality but no denoising.)
  for column_index in range(table_widget.columnCount()):
    item = table_widget.item(row_index, column_index)
    if item is None:
      continue
    if color == QColor(COLORS["green"]):
      # If the background is already yellow or read means that there was a
      # warning or an error in the render job and therefore not coloring it
      # green.
      if item.background() == QColor(COLORS["yellow"]):
        continue
      if item.background() == QColor(COLORS["red"]):
        continue
    if color == QColor(COLORS["yellow"]):
      if item.background() == QColor(COLORS["red"]):
        continue
    table_widget.blockSignals(True)
    item.setBackground(color)
    ui_utils.set_checkbox_background_color(
        table_widget, row_index, color)
    table_widget.blockSignals(False)


def set_background_colors(table_widget: QTableWidget, exit_code: int,
                          row_index: int, previous_job: int = 1) -> None:
  """Set the background colors of the rows.

  Args:
    exit_code: The exit code of the previous job. 0 means success, 664 means
      job was skipped, other values mean error.
    row_index: The row index of the current job.
    previous_job: The row index of the previous job. Needed because jobs can
      inactive and therefore skipped.
  Returns:
    None
  """
  color_row_background(table_widget,
                       row_index,
                       QColor(COLORS["blue_grey_lighter"]))
  if exit_code == 0:
    color_row_background(table_widget,
                         row_index - previous_job,
                         QColor(COLORS["green"]))
  elif exit_code == 664:
    color_row_background(table_widget,
                         row_index - previous_job,
                         QColor(COLORS["grey_light"]))
  elif exit_code == 987:
    color_row_background(table_widget,
                         row_index - previous_job,
                         QColor(COLORS["yellow"]))
  else:
    color_row_background(table_widget,
                         row_index - previous_job,
                         QColor(COLORS["red"]))


def reset_all_backgruond_colors(table_widget: QTableWidget) -> None:
  """Reset the background colors of all rows."""
  for row_index in range(table_widget.rowCount()):
    color_row_background(table_widget,
                         row_index, QColor(COLORS["grey_light"]))
