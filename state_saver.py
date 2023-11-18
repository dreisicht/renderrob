"""Class to provide storing methods to the render rob proto class.

Note: Only the state of the table is being handled here. The state of the settings
is being handled in the settings window class.
"""
from PySide6.QtCore import Qt
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
      # table_utils.post_process_row(table, i)
      ui_utils.add_line_edit(table, i, 1, text=render_job.file,
                             placeholder="File", alignment=Qt.AlignLeft | Qt.AlignVCenter)
      ui_utils.add_line_edit(table, i, 2, text=render_job.camera, placeholder="Camera")
      ui_utils.add_line_edit(table, i, 3, text=str(render_job.start), placeholder="Start")
      ui_utils.add_line_edit(table, i, 4, text=str(render_job.end), placeholder="End")
      ui_utils.add_line_edit(table, i, 5, text=str(render_job.x_res), placeholder="X")
      ui_utils.add_line_edit(table, i, 6, text=str(render_job.y_res), placeholder="Y")
      ui_utils.add_line_edit(table, i, 7, text=str(render_job.samples), placeholder="Samples")
      ui_utils.add_line_edit(table, i, 15, text=render_job.scene, placeholder="Scene")
      ui_utils.add_line_edit(table, i, 16, text=";".join(
          render_job.view_layers), placeholder="View Layers")
      ui_utils.add_line_edit(table, i, 17, text=render_job.comments, placeholder="Comments")
      ui_utils.add_checkbox(table, i, 0, checked=True)
      ui_utils.add_dropdown(table, i, 8, ui_utils.FILE_FORMATS_UI)
      ui_utils.add_dropdown(table, i, 9, ui_utils.RENDER_ENGINES)
      ui_utils.add_dropdown(table, i, 10, ui_utils.DEVICES)
      ui_utils.add_checkbox(table, i, 11, checked=render_job.motion_blur)
      ui_utils.add_checkbox(table, i, 12, checked=render_job.overwrite)
      ui_utils.add_checkbox(table, i, 13, checked=render_job.high_quality)
      ui_utils.add_checkbox(table, i, 14, checked=render_job.denoise)
      ui_utils.set_combobox_indexes(table, i, [render_job.file_format,
                                               render_job.engine,
                                               render_job.device])

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
