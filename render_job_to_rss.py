"""Build a Python command to execute the render_settings_setter."""

import os

from proto import state_pb2
from utils import ui_utils


def render_job_to_render_settings_setter(render_job: state_pb2.render_job, settings: state_pb2.settings) -> str:
  """Build a Python command to execute the render_settings_setter."""
  if render_job.high_quality:
    resolution = 100
    frame_step = 1
    samples = render_job.samples
  else:
    resolution = settings.preview.resolution if settings.preview.resolution_use else 100
    frame_step = settings.preview.frame_step if settings.preview.frame_step_use else 1
    samples = settings.preview.samples if settings.preview.samples_use else render_job.samples

  cwd = os.getcwd().replace("\\", "/")
  addons = []
  for addon in settings.addons:
    if addon:
      addons.append(addon)

  # Set the resolution to an empty string if it is not set, otherwise a syntax error will occur.
  x_res = render_job.x_res if render_job.x_res else '\"\"'
  y_res = render_job.y_res if render_job.y_res else '\"\"'
  samples = samples if samples else '\"\"'

  python_command = ['import sys',
                    f"sys.path.append(\'{cwd}\')",
                    "import render_settings_setter",
                    f"rss = render_settings_setter.RenderSettingsSetter(\'{render_job.scene}\', {render_job.view_layers})",
                    f"rss.activate_addons({addons})",
                    f"rss.set_camera(\'{render_job.camera}\')",
                    f"rss.set_render_settings(render_device=\'{ui_utils.DEVICES[render_job.device]}\', border={not render_job.high_quality}, samples={samples}, motion_blur={render_job.motion_blur}, engine=\'{ui_utils.RENDER_ENGINES[render_job.engine]}\')",
                    f"rss.set_denoising_settings(an_denoise={render_job.animation_denoise}, denoise={render_job.denoise})",
                    f"rss.set_output_settings(frame_step={frame_step}, xres={x_res}, yres={y_res}, percres={resolution}, high_quality={render_job.high_quality}, overwrite={render_job.overwrite})",
                    ]
  return " ; ".join(python_command)