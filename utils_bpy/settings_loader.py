"""Module executed in Blender to get the render_job settings."""

import json

import bpy  # pylint: disable=import-error

from utils_common import print_utils


def save_settings():
  """Save the render_job settings to the render_job proto."""

  render_job = {}

  render_job['file'] = bpy.data.filepath
  render_job['active'] = True
  render_job['camera'] = bpy.context.scene.camera.name
  render_job['start'] = str(bpy.context.scene.frame_start)
  render_job['end'] = str(bpy.context.scene.frame_end)
  render_job['x_res'] = str(bpy.context.scene.render.resolution_x)
  render_job['y_res'] = str(bpy.context.scene.render.resolution_y)
  engine = bpy.context.scene.render.engine
  if engine == "CYCLES":
    render_job['samples'] = str(bpy.context.scene.cycles.samples)
  else:
    render_job['samples'] = str(bpy.context.scene.eevee.taa_render_samples)

  if bpy.context.scene.cycles.device == "GPU":
    render_job['device'] = "gpu"
  else:
    render_job['device'] = "cpu"
  render_job['engine'] = engine.lower()
  render_job['motion_blur'] = bpy.context.scene.render.use_motion_blur
  render_job['overwrite'] = bpy.context.scene.render.use_overwrite
  render_job['high_quality'] = not bpy.context.scene.render.use_stamp
  render_job['denoise'] = bpy.context.scene.cycles.use_denoising
  render_job['scene'] = bpy.context.scene.name
  render_job['view_layers'] = [vl.name for vl in bpy.context.scene.view_layers if vl.use]
  render_job['file_format'] = bpy.context.scene.render.image_settings.file_format.lower()

  with open('.sync.json', 'w', encoding="utf-8") as f:
    json.dump(render_job, f)


save_settings()
print_utils.print_info("Settings saved.")
