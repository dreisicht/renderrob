"""Class to provide storing methods to the render rob proto class.

Note: Only the state of the table is being handled here. The state of the settings
is being handled in the settings window class.
"""
import os

from PySide6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox

from proto import state_pb2
from utils import table_utils, ui_utils


def get_text(item: QTableWidgetItem, widget=None) -> str:
  """Get the text from a table item."""
  if not item:
    return ""
  if widget == "dropdown":
    return item.currentText()
  if widget == "checkbox":
    return item.findChild(QCheckBox).isChecked()
  return item.text()


class StateSaver:
  """Class to provide storing methods to the render rob proto class."""

  def __init__(self):
    """Initialize the state saver."""
    self.state = state_pb2.render_rob_state()  # pylint: disable=no-member
    self.parent_widget = None

  def state_to_table(self, table: QTableWidget) -> None:
    """Load the state into a table."""
    for _ in range(table.rowCount()):
      table.removeRow(0)
    for i, render_job in enumerate(self.state.render_jobs):
      table.insertRow(i)

      table_utils.post_process_row(table, i)
      table.setItem(i, 1, QTableWidgetItem(render_job.file))
      table.setItem(i, 2, QTableWidgetItem(render_job.camera))
      table.setItem(i, 3, QTableWidgetItem(str(render_job.start)))
      table.setItem(i, 4, QTableWidgetItem(str(render_job.end)))
      table.setItem(i, 5, QTableWidgetItem(str(render_job.x_res)))
      table.setItem(i, 6, QTableWidgetItem(str(render_job.y_res)))
      table.setItem(i, 7, QTableWidgetItem(str(render_job.samples)))
      ui_utils.set_checkbox_values(table, i, [render_job.active,
                                              render_job.motion_blur,
                                              render_job.overwrite,
                                              render_job.high_quality,
                                              render_job.animation_denoise,
                                              render_job.denoise])
      ui_utils.set_combobox_indexes(table, i, [render_job.file_format,
                                               render_job.engine,
                                               render_job.device])
      table.setItem(i, 16, QTableWidgetItem(render_job.scene))
      table.setItem(i, 17, QTableWidgetItem(";".join(render_job.view_layers)))
      table.setItem(i, 18, QTableWidgetItem(render_job.comments))
      table_utils.set_text_alignment(table, i)

  def table_to_state(self, table: QTableWidget) -> None:
    """Create a render job from a table row."""
    del self.state.render_jobs[:]
    assert self.parent_widget
    for i in range(table.rowCount()):
      render_job = state_pb2.render_job()  # pylint: disable=no-member
      render_job.active = get_text(table.cellWidget(i, 0), widget="checkbox")
      #  #9 Do the file post-processing when the user enters a path.
      render_job.file = get_text(table.item(i, 1)).replace('"', "").replace("\\", "/")
      if "/" not in render_job.file:
        render_job.file = os.path.join(self.state.settings.blender_files_path, render_job.file)
      if not render_job.file:
        QMessageBox.warning(self.parent_widget, "Warning",
                            "The file path cannot be empty.", QMessageBox.Ok)
      if not os.path.exists(render_job.file):
        QMessageBox.warning(
            self.parent_widget, "Warning", f"The file path \"{render_job.file}\" does not exist.", QMessageBox.Ok)
      render_job.camera = get_text(table.item(i, 2))

      # NOTE: The values are strings and not ints, since the user can leave the
      # fields empty.
      render_job.start = get_text(table.item(i, 3))
      render_job.end = get_text(table.item(i, 4))
      render_job.x_res = get_text(table.item(i, 5))
      render_job.y_res = get_text(table.item(i, 6))
      render_job.samples = get_text(table.item(i, 7))

      render_job.file_format = get_text(table.cellWidget(i, 8), widget="dropdown")
      render_job.engine = get_text(table.cellWidget(i, 9), widget="dropdown")
      render_job.device = get_text(table.cellWidget(i, 10), widget="dropdown")
      render_job.motion_blur = get_text(table.cellWidget(i, 11), widget="checkbox")
      render_job.overwrite = get_text(table.cellWidget(i, 12), widget="checkbox")
      render_job.high_quality = get_text(table.cellWidget(i, 13), widget="checkbox")
      render_job.animation_denoise = get_text(table.cellWidget(i, 14), widget="checkbox")
      render_job.denoise = get_text(table.cellWidget(i, 15), widget="checkbox")
      render_job.scene = get_text(table.item(i, 16))
      del render_job.view_layers[:]
      new_view_layer_list = get_text(table.item(i, 17)).split(";")
      render_job.view_layers.extend(new_view_layer_list)
      render_job.comments = get_text(table.item(i, 18))
      self.state.render_jobs.append(render_job)


STATESAVER = StateSaver()
