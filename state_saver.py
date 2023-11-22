"""Class to provide storing methods to the render rob proto class.

Note: Only the state of the table is being handled here. The state of the settings
is being handled in the settings window class.
"""
import json

from PySide6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem

from proto import state_pb2
from utils import path_utils, table_utils, ui_utils


def get_text(item: QTableWidgetItem, widget=None) -> str:
  """Get the text from a table item."""
  if not item:
    return ""
  if widget == "dropdown":
    return item.currentText().replace(" ", "_")
  if widget == "checkbox":
    return item.findChild(QCheckBox).isChecked()
  return item.text()


def init_settings(state: state_pb2.render_rob_state) -> None:  # pylint: disable=no-member
  """Initialize the settings."""
  state.settings.blender_path = path_utils.discover_blender_path()
  state.settings.fps = 24
  state.settings.preview.samples = 16
  state.settings.preview.frame_step = 4
  state.settings.preview.resolution = 50


class StateSaver:
  """Class to provide storing methods to the render rob proto class."""

  def __init__(self):
    """Initialize the state saver."""
    self.state = state_pb2.render_rob_state()  # pylint: disable=no-member
    init_settings(self.state)

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
                                              render_job.denoise])
      ui_utils.set_combobox_indexes(table, i, [render_job.file_format,
                                               render_job.engine,
                                               render_job.device])
      table.setItem(i, 15, QTableWidgetItem(render_job.scene))
      table.setItem(i, 16, QTableWidgetItem(";".join(render_job.view_layers)))
      table.setItem(i, 17, QTableWidgetItem(render_job.comments))
      table_utils.set_text_alignment(table, i)

  def table_to_state(self, table: QTableWidget) -> None:
    """Create a render job from a table row."""

    del self.state.render_jobs[:]
    for i in range(table.rowCount()):
      render_job = state_pb2.render_job()  # pylint: disable=no-member
      render_job.active = get_text(table.cellWidget(i, 0), widget="checkbox")
      render_job.file = get_text(table.item(i, 1))
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
      # render_job.animation_denoise = get_text(table.cellWidget(i, 14), widget="checkbox")
      render_job.denoise = get_text(table.cellWidget(i, 14), widget="checkbox")
      render_job.scene = get_text(table.item(i, 15))
      del render_job.view_layers[:]
      new_view_layer_list = get_text(table.item(i, 16)).split(";")
      render_job.view_layers.extend(new_view_layer_list)
      render_job.comments = get_text(table.item(i, 17))
      self.state.render_jobs.append(render_job)

  def load_job_from_json(self, json_path: str) -> state_pb2.render_job:  # pylint: disable=no-member
    """Load the state from a json file."""
    with open(json_path, "r", encoding="utf-8") as json_file:
      json_state = json.loads(json_file.read())
    render_job = state_pb2.render_job()  # pylint: disable=no-member
    render_job.file = json_state["file"]
    render_job.active = json_state["active"]
    render_job.camera = json_state["camera"]
    render_job.start = json_state["start"]
    render_job.end = json_state["end"]
    render_job.x_res = json_state["x_res"]
    render_job.y_res = json_state["y_res"]
    render_job.samples = json_state["samples"]
    render_job.device = json_state["device"]
    render_job.engine = json_state["engine"]
    render_job.motion_blur = json_state["motion_blur"]
    render_job.overwrite = json_state["overwrite"]
    render_job.high_quality = json_state["high_quality"]
    render_job.denoise = json_state["denoise"]
    render_job.scene = json_state["scene"]
    render_job.view_layers.extend(json_state["view_layers"])
    render_job.file_format = json_state["file_format"]
    return render_job
