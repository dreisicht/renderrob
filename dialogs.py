import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QIcon, QPixmap


class ErrorDialog(QDialog):
  def __init__(self, message, parent=None):
    # TODO: Build a custom error dialog with Qt Designer.
    super(ErrorDialog, self).__init__(parent)
    self.setWindowTitle("Error")
    # Replace with your icon file path
    self.setWindowIcon(QIcon('path_to_your_icon.png'))
    self.setStyleSheet("background-color: #f2f2f2;")

    layout = QVBoxLayout(self)

    label = QLabel(message)
    # label.setStyleSheet("font-size: 14px; color: #555555;")
    layout.addWidget(label)

    ok_button = QPushButton("OK")
    # ok_button.setStyleSheet(
    #     "background-color: #0078d7; color: #ffffff; font-weight: bold; padding: 6px;")
    layout.addWidget(ok_button)

    ok_button.clicked.connect(self.close)
    self.exec_()
