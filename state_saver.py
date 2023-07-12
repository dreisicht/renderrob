"""Class to provide storing methods to proto classes."""
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from proto import state_pb2
import utils.ui_utils as ui_utils


class StateSaver:
  """Class to provide storing methods to proto classes."""

  def __init__(self):
    """Initialize the state saver."""
    self._state = None

  def state_to_table(table: QTableWidget, state: state_pb2):
    """Load the state into a table."""
    for i in range(table.rowCount()):
      table.removeRow(0)
    for i, render_job in enumerate(state.render_jobs):
      table.insertRow(i)
      post_process_row(table, i)
      ui_utils.set_checkbox_values(table, i, [render_job.active,
                                              render_job.motion_blur,
                                              render_job.new_version,
                                              render_job.high_quality,
                                              render_job.animation_denoise,
                                              render_job.denoise])

      if render_job.file_format not in ui_utils.FILE_FORMATS or \
              render_job.engine not in ui_utils.RENDER_ENGINES or \
              render_job.device not in ui_utils.DEVICES:
        raise ValueError("Error: Invalid file format, render engine, or device.")
      file_format_id = ui_utils.FILE_FORMATS.index(render_job.file_format)
      render_engine_id = ui_utils.RENDER_ENGINES.index(render_job.engine)
      device_id = ui_utils.DEVICES.index(render_job.device)
      ui_utils.set_combobox_indexes(
          table, i, [file_format_id, render_engine_id, device_id])

      table.setItem(i, 1, QTableWidgetItem(render_job.file))
      table.setItem(i, 2, QTableWidgetItem(render_job.camera))
      table.setItem(i, 3, QTableWidgetItem(render_job.start))
      table.setItem(i, 4, QTableWidgetItem(render_job.end))
      table.setItem(i, 5, QTableWidgetItem(render_job.x_res))
      table.setItem(i, 6, QTableWidgetItem(render_job.y_res))
      table.setItem(i, 7, QTableWidgetItem(render_job.samples))
      table.setItem(i, 16, QTableWidgetItem(render_job.scene))
      table.setItem(i, 17, QTableWidgetItem(render_job.view_layer))
      table.setItem(i, 18, QTableWidgetItem(render_job.comments))
      # table_utils.post_process_row(table, i)

  def table_to_state(table: QTableWidget, state: state_pb2):
    """Save the state to a table."""
    state.render_jobs = list(jobs_from_table_widget(table))
