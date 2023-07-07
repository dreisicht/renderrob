"""Data structure for storing render job information."""

from __future__ import annotations

from typing import List

from PySide6.QtWidgets import (QCheckBox, QComboBox, QTableWidget,
                               QTableWidgetItem)
import table_utils


class RenderJob():
  """Data structure for storing render job information."""

  def __init__(self) -> None:
    """Initialize the render job."""
    self.active: bool = True
    self.file: str = ""
    self.camera: str = ""
    self.start: str = ""
    self.end: str = ""
    self.x_res: str = ""
    self.y_res: str = ""
    self.samples: str = ""
    self.file_format: str = ""
    self.engine: str = ""
    self.device: str = ""
    self.motion_blur: bool = False
    self.new_version: bool = False
    self.high_quality: bool = False
    self.animation_denoise: bool = False
    self.denoise: bool = False
    self.scene: str = ""
    self.view_layer: str = ""
    self.comments: str = ""

  def from_row(self, table: QTableWidget, row: int) -> None:
    """Create a render job from a table row."""
    self.active = self.get_text(table.cellWidget(row, 0), widget="checkbox")
    self.file = self.get_text(table.item(row, 1))
    self.camera = self.get_text(table.item(row, 2))
    self.start = self.get_text(table.item(row, 3))
    self.end = self.get_text(table.item(row, 4))
    self.x_res = self.get_text(table.item(row, 5))
    self.y_res = self.get_text(table.item(row, 6))
    self.samples = self.get_text(table.item(row, 7))
    self.file_format = self.get_text(table.cellWidget(row, 8), widget="dropdown")
    self.engine = self.get_text(table.cellWidget(row, 9), widget="dropdown")
    self.device = self.get_text(table.cellWidget(row, 10), widget="dropdown")
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
      return item.currentText()
    if widget == "checkbox":
      return item.findChild(QCheckBox).isChecked()
    return item.text()

  def to_dict(self):
    """Convert the render job to a dictionary."""
    result = {}
    for key, value in self.__dict__.items():
      result[key] = value
    return result


def jobs_from_table_widget(table: QTableWidget) -> List[RenderJob]:
  """Get all render jobs from a table widget."""
  for i in range(table.rowCount()):
    rjb = RenderJob()
    rjb.from_row(table, i)
    yield rjb


def jobs_to_table_widget(table: QTableWidget, jobs: List[RenderJob]) -> None:
  """Set all render jobs in a table widget."""
  for i, job in enumerate(jobs):
    table.setRowCount(i + 1)
    table_utils.post_process_row(table, i)
    table.setItem(i, 1, QTableWidgetItem(job.file))
    table.setItem(i, 2, QTableWidgetItem(job.camera))
    table.setItem(i, 3, QTableWidgetItem(job.start))
    table.setItem(i, 4, QTableWidgetItem(job.end))
    table.setItem(i, 5, QTableWidgetItem(job.x_res))
    table.setItem(i, 6, QTableWidgetItem(job.y_res))
    table.setItem(i, 7, QTableWidgetItem(job.samples))
    table.setItem(i, 8, QTableWidgetItem(job.file_format))
    table.setItem(i, 9, QTableWidgetItem(job.engine))
    table.setItem(i, 10, QTableWidgetItem(job.device))
    # table.setCellWidget(i, 11, table_utils.make_checkbox(job.motion_blur))
    # table.setCellWidget(i, 12, table_utils.make_checkbox(job.new_version))
    # table.setCellWidget(i, 13, table_utils.make_checkbox(job.high_quality))
    # table.setCellWidget(i, 14, table_utils.make_checkbox(job.animation_denoise))
    # table.setCellWidget(i, 15, table_utils.make_checkbox(job.denoise))
    table.setItem(i, 16, QTableWidgetItem(job.scene))
    table.setItem(i, 17, QTableWidgetItem(job.view_layer))
    table.setItem(i, 18, QTableWidgetItem(job.comments))


if __name__ == "__main__":
  print(RenderJob().to_dict())
