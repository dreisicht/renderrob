import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QMainWindow, QVBoxLayout
from PySide6.QtCore import QMetaObject, Slot, QEvent
from utils import print_utils, table_utils, ui_utils


class ExampleWindow(QWidget):
  def __init__(self):
    super().__init__()

    self.setup()

  def setup(self):
    layout = QVBoxLayout()
    layout.addWidget(ui_utils.load_ui_from_file("ui/window.ui"))
    self.setLayout(layout)
    self.show()

  def closeEvent(self, event):
    """Handle the close event."""
    print("DEBUG")
    reply = QMessageBox.question(self, 'Message', 'Unsaved state. Quit?',
                                 QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Cancel)

    if reply == QMessageBox.Close:
      event.accept()
    else:
      event.ignore()


def run():
  app = QApplication(sys.argv)

  exw = ExampleWindow()

  sys.exit(app.exec())


if __name__ == '__main__':
  run()
