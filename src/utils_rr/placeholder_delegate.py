"""Placeholder delegate for QTableWidget."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyledItemDelegate, QTableWidget

from utils_rr import ui_utils


class PlaceholderDelegate(QStyledItemDelegate):
  """Placeholder delegate for QTableWidget."""

  def __init__(self, placeholder_text, parent=None):
    super().__init__(parent)
    self.placeholder_text = placeholder_text

  def paint(self, painter, option, index):
    """Paint the placeholder text."""
    super().paint(painter, option, index)

    if not index.data():
      placeholder_rect = option.rect.adjusted(2, 0, 0, 0)
      painter.setPen(QColor("#c0c0c0"))
      painter.drawText(placeholder_rect, Qt.AlignHCenter | Qt.AlignVCenter, self.placeholder_text)


def setup_placeholder_delegate(table_widget: QTableWidget):
  """Set up the placeholder delegate for the given table widget."""
  table_widget.blockSignals(True)
  for row in range(table_widget.rowCount()):
    for col in ui_utils.TEXT_COLUMNS + ui_utils.NUMBER_COLUMNS:
      item = table_widget.item(row, col)
      if item:
        placeholder_text = ui_utils.PLACEHOLDER_TEXT[col]
        item.setData(Qt.EditRole, placeholder_text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item_delegate = PlaceholderDelegate(placeholder_text, table_widget)
        table_widget.setItemDelegateForColumn(col, item_delegate)
  table_widget.blockSignals(False)
