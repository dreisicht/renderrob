"""Helper class to be able to register events for drag and drop operations."""

from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QWidget

from utils_rr import table_utils


class DropWidget(QWidget):
  """Helper class to be able to register events for drag and drop operations."""

  def __init__(self, parent: QWidget | None = None) -> None:
    super().__init__(parent)
    self.setAcceptDrops(True)

  def dropEvent(self, event: QDropEvent) -> None:
    """Add every dropped .blend file as a new row."""
    if event.mimeData().hasUrls:
      for url in event.mimeData().urls():
        file_path = url.toLocalFile()
        if not url.isLocalFile():
          continue
        table = self.parent().tableWidget
        table_utils.add_file_below(table, file_path)
        table.itemChanged.emit(table.item(table.rowCount() - 1, 1))
        event.accept()
    else:
      event.ignore()

  def dragEnterEvent(self, event: QDragEnterEvent) -> None:
    """Accept the drag only if it carries at least one .blend file."""
    mime_data = event.mimeData()
    if mime_data.hasUrls():
      urls = mime_data.urls()
      for url in urls:
        file_path = url.toLocalFile()
        if file_path.endswith(".blend"):
          event.acceptProposedAction()
          return
    event.ignore()

  def dragMoveEvent(self, event: QDragMoveEvent) -> None:
    """Accept the move so the drop event is delivered."""
    event.accept()
