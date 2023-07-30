"""Utility functions for table operations."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QStyledItemDelegate, QComboBox, QCheckBox, QWidget
import utils.ui_utils as ui_utils

TABLE = None
# Note: This variable is required because when using clicked.connect() the argument is
# only the function. Therefore arguments to the function cannot be passed.


def make_editable(table_widget: QTableWidget) -> None:
  """Undo the make QTableWidget only selectable."""
  class EditableDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
      # Allow editing by returning the default editor
      return QStyledItemDelegate.createEditor(self, parent, option, index)
  delegate = EditableDelegate()
  table_widget.setItemDelegate(delegate)
  for row in range(table_widget.rowCount()):
    for col in ui_utils.COMBOBOX_COLUMNS:
      widget = table_widget.cellWidget(row, col)
      if widget and isinstance(widget, QComboBox):
        widget.setDisabled(False)
      # FIXME: Restore previous value of dropdown menu.

    for col in ui_utils.CHECKBOX_COLUMNS:
      widget = table_widget.cellWidget(row, col)
      checkbox_item = widget.findChild(QCheckBox)
      checked = checkbox_item.isChecked()
      if widget and isinstance(widget, QWidget):
        # checkbox_item.setCheckable(True)
        checkbox_item.setDisabled(False)

        # checkbox_item.setChecked(checked)


def make_read_only_selectable(table_widget):
  """Make QTableWidget only selectable."""
  # TODO: #10 Set the render button to disabled.
  class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
      # Prevent editing by returning None when an editor is requested
      return None
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
  # TODO: #11 Add undo functionality.
  current_row = TABLE.currentRow()
  if current_row == -1:
    current_row = TABLE.rowCount() - 1
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
       "Overwrite",
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
      item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    else:
      item.setTextAlignment(Qt.AlignCenter)
    table.setItem(row, i, item)
