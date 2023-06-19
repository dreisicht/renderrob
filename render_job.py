"""Data structure for storing render job information."""

from __future__ import annotations
from typing import List
from PySide6.QtWidgets import QTableWidgetItem, QComboBox, QCheckBox


class RenderJob():
  """Data structure for storing render job information."""

  def __init__(self, table, row) -> None:
    """Initialize the render job."""
    self.active = self.get_text(table.cellWidget(row, 0), widget="checkbox")
    self.file = self.get_text(table.item(row, 1))
    self.camera = self.get_text(table.item(row, 2))
    self.start = self.get_text(table.item(row, 3))
    self.end = self.get_text(table.item(row, 4))
    self.x_res = self.get_text(table.item(row, 5))
    self.y_res = self.get_text(table.item(row, 6))
    self.samples = self.get_text(table.item(row, 7))
    self.file_format = self.get_text(table.item(row, 8), widget="dropdown")
    self.engine = self.get_text(table.item(row, 9), widget="dropdown")
    self.device = self.get_text(table.item(row, 10), widget="dropdown")
    self.motion_blur = self.get_text(table.cellWidget(row, 11), widget="checkbox")
    self.new_version = self.get_text(table.cellWidget(row, 12), widget="checkbox")
    self.high_quality = self.get_text(table.cellWidget(row, 13), widget="checkbox")
    self.animation_denoise = self.get_text(table.cellWidget(row, 14), widget="checkbox")
    self.denoise = self.get_text(table.cellWidget(row, 15), widget="checkbox")
    self.scene = self.get_text(table.item(row, 16))
    self.view_layer = self.get_text(table.item(row, 17))
    self.comments = self.get_text(table.item(row, 18))

  def get_text(self, item: QTableWidgetItem, widget=None) -> str:
    """Get the text from a table item."""
    if not item:
      return ""
    if widget == "dropdown":
      return item.findChild(QComboBox).currentText()
    if widget == "checkbox":
      return item.findChild(QCheckBox).isChecked()
    return item.text()


def render_jobs_from_table_widget(table) -> List[RenderJob]:
  """Get all render jobs from a table widget."""
  for i in range(table.rowCount()):
    yield RenderJob(table, i)
