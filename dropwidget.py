"""Helper class to be able to register events for drag and drop operations."""

from PySide6.QtWidgets import QWidget
from utils import table_utils


class DropWidget(QWidget):
  """Helper class to be able to register events for drag and drop operations."""

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setAcceptDrops(True)

  def dropEvent(self, event):
    if event.mimeData().hasUrls:
      for url in event.mimeData().urls():
        file_path = url.toLocalFile()
        if not url.isLocalFile():
          continue
        if not file_path.endswith('.blend'):
          continue
        table_utils.add_file_below(file_path)
        event.accept()
    else:
      event.ignore()

  def dragEnterEvent(self, event):
    mime_data = event.mimeData()
    if mime_data.hasUrls():
      urls = mime_data.urls()
      for url in urls:
        file_path = url.toLocalFile()
        if file_path.endswith('.blend'):
          event.acceptProposedAction()
          return
    event.ignore()

  def dragMoveEvent(self, event):
    event.accept()
