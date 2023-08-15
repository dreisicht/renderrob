"""Provides custom dialogs for the application."""
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class ErrorDialog(QDialog):
  """A custom error dialog."""

  def __init__(self, message, parent=None):
    """Initialize the error dialog."""
    #  #4 Build a custom error dialog with Qt Designer.
    super(ErrorDialog, self).__init__(parent)
    self.setWindowTitle("Error")
    self.setWindowIcon(QIcon('icons/icon.ico'))
    self.setStyleSheet("background-color: #f2f2f2;")
    layout = QVBoxLayout(self)
    label = QLabel(message)
    layout.addWidget(label)
    ok_button = QPushButton("OK")
    layout.addWidget(ok_button)
    ok_button.clicked.connect(self.close)
    self.exec_()
