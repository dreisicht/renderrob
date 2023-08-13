"""Unit tests for shot_name_builder.py."""

import unittest
from proto import state_pb2
import render_job_to_rss


class TestRenderJobToRss(unittest.TestCase):
  """Tests for the ShotNameBuilder class."""

  def test_render_job_to_render_settings_setter(self) -> None:
    """Test that the shot name is built correctly."""
    render_job = state_pb2.render_job()
    render_job.file = "/home/rob/Projects/RenderRob/rr_test.blend"
    render_job.active = True
    render_job.camera = "Camera"
    render_job.start = str(1)
    render_job.end = str(250)
    render_job.x_res = str(1920)
    render_job.y_res = str(1080)
    render_job.samples = str(128)
    render_job.file_format = 0
    render_job.engine = 0
    render_job.device = 0
    render_job.motion_blur = True
    render_job.overwrite = True
    render_job.high_quality = True
    render_job.animation_denoise = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    settings = state_pb2.settings()
    rss = render_job_to_rss.render_job_to_render_settings_setter(
        render_job, settings)
    self.assertEqual(
        rss, "import sys ; sys.path.append('c:/Users/peter/Documents/repositories/RenderRob') ; import render_settings_setter ; rss = render_settings_setter.RenderSettingsSetter('Scene', ['View Layer']) ; rss.activate_addons([]) ; rss.set_camera('Camera') ; rss.set_render_settings(render_device='gpu', border=False, samples=128, motion_blur=True, engine='cycles') ; rss.set_denoising_settings(an_denoise=True, denoise=True) ; rss.set_output_settings(frame_step=1, xres=1920, yres=1080, percres=100, high_quality=True, overwrite=True)")
