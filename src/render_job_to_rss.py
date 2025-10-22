"""Build a Python command to execute the render_settings_setter."""

import os
import sys
from pathlib import Path

from protos import state_pb2
from utils_rr import ui_utils
from utils_rr.path_utils import normalize_drive_letter


def render_job_to_render_settings_setter(
  render_job: state_pb2.render_job,  # pylint: disable=no-member
  settings: state_pb2.settings,
) -> str:  # pylint: disable=no-member
  """Build a Python command to execute the render_settings_setter."""
  if render_job.high_quality:
    resolution = 100
    frame_step = 1
    samples = render_job.samples
  else:
    resolution = settings.preview.resolution if settings.preview.resolution_use else 100
    frame_step = settings.preview.frame_step if settings.preview.frame_step_use else 1
    samples = settings.preview.samples if settings.preview.samples_use else render_job.samples

  if sys.platform == "darwin":
    cwd = Path.cwd() / "../Resources/"
  else:
    cwd = normalize_drive_letter(os.getcwd())

  addons = list(settings.addons)

  # Set the resolution to an empty string if it is not set, otherwise a syntax error will occur.
  x_res = render_job.x_res if render_job.x_res else '""'
  y_res = render_job.y_res if render_job.y_res else '""'
  samples = samples if samples else '""'

  python_command = [
    "import sys",
    f"sys.path.append('{cwd}')",
    "from utils_bpy import render_settings_setter",
    f"rss = render_settings_setter.RenderSettingsSetter('{render_job.scene}', {render_job.view_layers})",  # noqa: E501
    f"rss.activate_addons({addons})",
    f"rss.set_camera('{render_job.camera}')",
    f"rss.set_render_settings(render_device='{ui_utils.DEVICES[render_job.device]}', border={not render_job.high_quality}, samples={samples}, motion_blur={render_job.motion_blur}, engine='{ui_utils.RENDER_ENGINES[render_job.engine]}')",  # noqa: E501
    f"rss.set_denoising_settings(denoise={render_job.denoise})",
    f"rss.set_output_settings(frame_step={frame_step}, xres={x_res}, yres={y_res}, percres={resolution}, high_quality={render_job.high_quality})",  # noqa: E501
    "rss.custom_commands()",
  ]
  return " ; ".join(python_command)
