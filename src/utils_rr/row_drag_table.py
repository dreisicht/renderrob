"""A table whose rows can be reordered by dragging them."""

from PySide6.QtCore import QMimeData, QPoint, QRect, Qt, Signal
from PySide6.QtGui import (
  QColor,
  QCursor,
  QDrag,
  QDragEnterEvent,
  QDragLeaveEvent,
  QDragMoveEvent,
  QDropEvent,
  QPainter,
  QPaintEvent,
  QPen,
  QPixmap,
)
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QWidget

from utils_rr import table_utils

# A row drag carries its source row under Render Rob's own format, so that the .blend files the
# main window accepts stay distinguishable from a reorder.
ROW_MIME_TYPE = "application/x-renderrob-row"

DROP_INDICATOR_WIDTH = 3
# The dragged row is carried along under the cursor, faded enough to read the table through it.
DRAG_PIXMAP_OPACITY = 0.75


def drop_row_at(table: QTableWidget, y: int) -> int:
  """Return the row a drop at the given position in the viewport would insert in front of.

  A drop in the upper half of a row lands above it and one in the lower half below it, so the
  result counts the rows as they are before the move and ranges from 0 to the row count.
  """
  row = table.rowAt(y)
  if row < 0:
    # Everything below the last row drops at the end of the table.
    return table.rowCount()
  if y >= table.rowViewportPosition(row) + table.rowHeight(row) / 2:
    return row + 1
  return row


def drop_indicator_y(table: QTableWidget, drop_row: int) -> int:
  """Return the height in the viewport at which the insertion line for a drop is drawn."""
  if drop_row < table.rowCount():
    y = table.rowViewportPosition(drop_row)
  elif table.rowCount():
    last_row = table.rowCount() - 1
    y = table.rowViewportPosition(last_row) + table.rowHeight(last_row)
  else:
    y = 0
  # A line drawn exactly on an edge of the viewport would be half cut off.
  margin = DROP_INDICATOR_WIDTH // 2 + 1
  return min(max(y, margin), table.viewport().height() - margin)


def destination_for_drop(source_row: int, drop_row: int) -> int:
  """Turn an insertion point into the index the dragged row ends up at.

  drop_row counts the rows as they are before the move, so every row below the dragged one moves
  up by one once it has been taken out of the table.
  """
  if drop_row > source_row:
    return drop_row - 1
  return drop_row


class RowDragTableWidget(QTableWidget):
  """A table whose rows the user can reorder by dragging them.

  The widget only reports the move. Reordering has to happen on the render jobs behind the table,
  since every row carries checkboxes and dropdowns as cell widgets that an item-level move would
  leave behind - main.py connects rows_reordered to table_utils.move_row.
  """

  # (source row, destination row), the latter being where the row ends up once it has been taken
  # out of the table - what table_utils.move_row expects.
  rows_reordered = Signal(int, int)

  def __init__(self, parent: QWidget | None = None) -> None:
    super().__init__(parent)
    self.setDragEnabled(True)
    self.setAcceptDrops(True)
    self.setDragDropMode(QAbstractItemView.InternalMove)
    self.setDefaultDropAction(Qt.MoveAction)
    # Qt's own indicator marks the cell under the cursor, which says nothing about where a whole
    # row would land; paintEvent draws a full width insertion line instead.
    self.setDropIndicatorShown(False)
    # Rows are moved between each other, never dropped onto each other.
    self.setDragDropOverwriteMode(False)
    # The row the insertion line is currently drawn in front of, or -1 while nothing is dragged.
    self._drop_row = -1

  ######### DRAG SOURCE #########
  def startDrag(self, supported_actions: Qt.DropActions) -> None:  # pylint: disable=invalid-name
    """Carry the row the user grabbed along under the cursor.

    Qt's own implementation drags the selected items and deletes them once the drop reports a
    move, which for a reorder would take the row's cell widgets with it. This one hands the row
    number to the drop site and leaves the table untouched.
    """
    del supported_actions  # A row can only ever be moved, never copied.
    row = self.currentRow()
    if row < 0:
      return
    mime_data = QMimeData()
    mime_data.setData(ROW_MIME_TYPE, str(row).encode())

    drag = QDrag(self)
    drag.setMimeData(mime_data)
    pixmap = self._row_pixmap(row)
    drag.setPixmap(pixmap)
    # Hold the row where it was grabbed, so it keeps sitting under the cursor.
    grab_position = self.viewport().mapFromGlobal(QCursor.pos())
    drag.setHotSpot(QPoint(grab_position.x(), self.rowHeight(row) // 2))
    drag.exec(Qt.MoveAction)

  def _row_pixmap(self, row: int) -> QPixmap:
    """Grab a row as it is painted, cell widgets included."""
    rect = QRect(0, self.rowViewportPosition(row), self.viewport().width(), self.rowHeight(row))
    grabbed = self.viewport().grab(rect)
    pixmap = QPixmap(grabbed.size())
    pixmap.setDevicePixelRatio(grabbed.devicePixelRatio())
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setOpacity(DRAG_PIXMAP_OPACITY)
    painter.drawPixmap(0, 0, grabbed)
    painter.end()
    return pixmap

  ######### DROP SITE #########
  @staticmethod
  def dragged_row(event: QDragEnterEvent | QDragMoveEvent | QDropEvent) -> int:
    """Return the row a Render Rob row drag carries, or -1 for any other kind of drag."""
    mime_data = event.mimeData()
    if not mime_data.hasFormat(ROW_MIME_TYPE):
      return -1
    try:
      return int(mime_data.data(ROW_MIME_TYPE).data().decode())
    except ValueError:
      return -1

  def _set_drop_row(self, row: int) -> None:
    """Move the insertion line, repainting only when it actually moved."""
    if row == self._drop_row:
      return
    self._drop_row = row
    self.viewport().update()

  def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # pylint: disable=invalid-name
    """Take a row drag, and the .blend files the window takes everywhere else.

    Qt hands a drag to the innermost widget that accepts drops and does not walk up from there,
    so once the table accepts drops at all, dropped files stop reaching the window behind it
    unless the table takes them itself.
    """
    if self.dragged_row(event) >= 0:
      event.setDropAction(Qt.MoveAction)
      event.accept()
      return
    if table_utils.carries_blend_file(event.mimeData()):
      event.acceptProposedAction()
      return
    event.ignore()

  def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # pylint: disable=invalid-name
    """Follow the cursor with the insertion line while a row is being dragged."""
    if self.dragged_row(event) < 0:
      # A file drag lands at the end of the table wherever it is dropped, so there is no
      # insertion line to show for it.
      event.acceptProposedAction()
      return
    self._set_drop_row(drop_row_at(self, event.position().toPoint().y()))
    event.setDropAction(Qt.MoveAction)
    event.accept()

  def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # pylint: disable=invalid-name
    """Take the insertion line away again once the drag has left the table."""
    self._set_drop_row(-1)
    event.accept()

  def dropEvent(self, event: QDropEvent) -> None:  # pylint: disable=invalid-name
    """Report where a dragged row was dropped, or add the files that were dropped instead."""
    source_row = self.dragged_row(event)
    if source_row < 0:
      if event.mimeData().hasUrls() and table_utils.add_dropped_files(self, event.mimeData()):
        event.acceptProposedAction()
        return
      event.ignore()
      return
    destination_row = destination_for_drop(
      source_row,
      drop_row_at(self, event.position().toPoint().y()),
    )
    self._set_drop_row(-1)
    event.setDropAction(Qt.MoveAction)
    event.accept()
    if destination_row != source_row:
      self.rows_reordered.emit(source_row, destination_row)

  ######### PAINTING #########
  def paintEvent(self, event: QPaintEvent) -> None:  # pylint: disable=invalid-name
    """Paint the table, and over it the line showing where a dragged row would land."""
    super().paintEvent(event)
    if self._drop_row < 0:
      return
    painter = QPainter(self.viewport())
    painter.setPen(QPen(QColor(table_utils.COLORS["accent"]), DROP_INDICATOR_WIDTH))
    y = drop_indicator_y(self, self._drop_row)
    painter.drawLine(0, y, self.viewport().width(), y)
    painter.end()
