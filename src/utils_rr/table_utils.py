"""Utility functions for table operations."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import (
  QCheckBox,
  QComboBox,
  QHeaderView,
  QStyledItemDelegate,
  QStyleOptionViewItem,
  QTableWidget,
  QTableWidgetItem,
  QWidget,
)

from utils_rr import path_utils, ui_utils

if TYPE_CHECKING:
  from state_saver import StateSaver

# The table operators notify the main window before and after they change the table.
TableCallback = Callable[[], None]

HEADER_HEIGHT = 44
MINIMUM_COLUMN_WIDTH = 46
# Columns that cannot size themselves usefully: the free-text ones are empty until they are filled
# in, and ResizeToContents ignores the width of a cell's combobox widget.
DEFAULT_COLUMN_WIDTHS = {
  1: 300,  # File
  2: 90,  # Camera
  8: 110,  # File Format
  9: 90,  # Engine
  10: 80,  # Device
  15: 90,  # Scene
  16: 110,  # View Layers
  17: 160,  # Comments
}

# The two palettes Render Rob renders with. Keys are shared, so the rest of the code can look a
# color up by meaning and stay theme-agnostic. Row colors sit behind the table's normal text, so
# each theme picks the lightness that keeps that text readable; the console colors are badges
# behind their own foreground and can be stronger.
COLORS_LIGHT = {
  # Status colors for table rows: blue while a job renders, green when it succeeded, yellow when it
  # reported warnings, red when it broke. They carry the whole status readout of the table, so they
  # stay saturated enough to tell apart at a glance while keeping $text readable on top.
  "red": 0xE0687F,
  "yellow": 0xF2C14E,
  "green": 0x86D2AA,
  "grey_light": 0xFFFFFF,
  "grey_inactive": 0xECEFF1,
  "blue_grey_lighter": 0x7FB6DB,
  # Brand colors.
  "blue": 0x57A3B4,
  "blue_grey": 0x4F7997,
  "blue_grey_darker": 0x345064,
  "grey_neutral": 0x999999,
  "black_light": 0x22282B,
  "black_dark": 0x1E2529,
  "white": 0xFFFFFF,
  # Window chrome.
  "window": 0xF2F4F6,
  "surface": 0xFFFFFF,
  "surface_alt": 0xF7F9FA,
  "border": 0xD8DEE3,
  "border_strong": 0xC2CCD3,
  "text": 0x1E2529,
  "text_muted": 0x6B7780,
  "header_background": 0xE8EDF1,
  "accent": 0x4F7997,
  "accent_hover": 0x5D8BAB,
  "accent_pressed": 0x3D6280,
  "accent_text": 0xFFFFFF,
  "danger": 0xA3324C,
  "danger_hover": 0xB93A57,
  "selection": 0xCFE0EC,
  # Console.
  "console_background": 0x1F2C36,
  "console_foreground": 0xDFE6EA,
  "console_info": 0x6397BD,
  "console_warning": 0xFFD966,
  "console_error": 0x98304A,
}

COLORS_DARK = {
  # Status colors for table rows, in the same four hues as the light palette, darkened until the
  # light $text on top of them is readable.
  "red": 0x8C2C42,
  "yellow": 0x7A5F18,
  "green": 0x2E7355,
  "grey_light": 0x272E33,
  "grey_inactive": 0x23292D,
  "blue_grey_lighter": 0x2E6488,
  # Brand colors.
  "blue": 0x57A3B4,
  "blue_grey": 0x4F7997,
  "blue_grey_darker": 0x345064,
  "grey_neutral": 0x94A1AA,
  "black_light": 0x22282B,
  "black_dark": 0xE3E8EB,
  "white": 0xE3E8EB,
  # Window chrome.
  "window": 0x20262A,
  "surface": 0x272E33,
  "surface_alt": 0x2C343A,
  "border": 0x3A444B,
  "border_strong": 0x4A565E,
  "text": 0xE3E8EB,
  "text_muted": 0x94A1AA,
  "header_background": 0x232A2F,
  "accent": 0x6397BD,
  "accent_hover": 0x74A7CB,
  "accent_pressed": 0x4F7997,
  "accent_text": 0x10171C,
  "danger": 0xC0455F,
  "danger_hover": 0xD05070,
  "selection": 0x35505F,
  # Console.
  "console_background": 0x171D21,
  "console_foreground": 0xD3DADE,
  "console_info": 0x4E7EA0,
  "console_warning": 0x8A7328,
  "console_error": 0x8C2C42,
}
# NOTE: This variable is being set from renderrob.py since we only know there if a dark or a
# light theme is requested.
COLORS = COLORS_DARK


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

    def createEditor(  # pylint: disable=invalid-name
      self,
      parent: QWidget,
      option: QStyleOptionViewItem,
      index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
      """Allow editing by returning the default editor."""
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

    # ty: ignore[invalid-method-override] - returning None is Qt's documented way to make a cell
    # uneditable, but PySide6's stub types the return as a plain QWidget.
    def createEditor(  # pylint: disable=invalid-name
      self,
      parent: QWidget,
      option: QStyleOptionViewItem,
      index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget | None:
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
        checkbox_item.setDisabled(True)
        checkbox_item.setChecked(checked)


# @operator
def move_row_down(
  table_widget: QTableWidget,
  before_callback_function: TableCallback,
  after_callback_function: TableCallback,
) -> None:
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
def move_row_up(
  table_widget: QTableWidget,
  before_callback_function: TableCallback,
  after_callback_function: TableCallback,
) -> None:
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
def duplicate_row(
  table_widget: QTableWidget,
  state_saver: "StateSaver",
  before_callback_function: TableCallback,
  after_callback_function: TableCallback,
) -> None:
  """Duplicate the currently selected row."""
  table_widget.blockSignals(True)
  before_callback_function()

  state_saver.table_to_state(table_widget)
  current_row = table_widget.currentRow()
  state_saver.state.render_jobs.insert(current_row + 1, state_saver.state.render_jobs[current_row])
  state_saver.state_to_table(table_widget)

  after_callback_function()
  table_widget.blockSignals(False)


# @operator
def add_row_below(
  table_widget: QTableWidget,
  before_callback_function: TableCallback | None = None,
  after_callback_function: TableCallback | None = None,
) -> None:
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
def remove_active_row(
  table_widget: QTableWidget,
  before_callback_function: TableCallback,
  after_callback_function: TableCallback,
) -> None:
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
  header.setMinimumHeight(HEADER_HEIGHT)
  header.setMinimumSectionSize(MINIMUM_COLUMN_WIDTH)
  header.setDefaultAlignment(Qt.AlignCenter)
  header.setHighlightSections(False)
  table_widget.verticalHeader().setHighlightSections(False)
  table_widget.setHorizontalHeaderLabels(
    [
      "Active",
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
    ]
  )

  # The numeric columns size themselves to their contents; the rest get a usable default width and
  # stay draggable, and the last column takes up whatever is left over.
  header.setSectionResizeMode(QHeaderView.ResizeToContents)
  for column, width in DEFAULT_COLUMN_WIDTHS.items():
    header.setSectionResizeMode(column, QHeaderView.Interactive)
    table_widget.setColumnWidth(column, width)
  header.setStretchLastSection(True)
  ui_utils.fill_row(table_widget, row)


def set_text_alignment(table_widget: QTableWidget, row: int) -> None:
  """Set the text alignment of the table items."""
  for i in range(table_widget.columnCount()):
    if i in ui_utils.COMBOBOX_COLUMNS or i in ui_utils.CHECKBOX_COLUMNS:
      continue
    old_item = table_widget.item(row, i)
    text = old_item.text() if old_item else ""
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
  # Taking the background color of the camera tableitem as reference. The item is missing while a
  # row is still being built up, in which case there is no previous color to preserve.
  reference_item = table_widget.item(row_index, 2)
  previous_color = reference_item.background() if reference_item else None

  color = base_color
  if previous_color == QColor(COLORS["red"]):
    color = QColor(COLORS["red"])
  elif previous_color == QColor(COLORS["yellow"]) and base_color == QColor(COLORS["green"]):
    color = QColor(COLORS["yellow"])

  for column_index in range(table_widget.columnCount()):
    item = table_widget.item(row_index, column_index)

    # Check if the value in the numbers columns is valid.
    if (
      item
      and item.text()
      and (column_index in ui_utils.NUMBER_COLUMNS and not item.text().isnumeric())
    ):
      item.setBackground(QColor(COLORS["red"]))
    elif item:
      item.setBackground(color)
