"""Unit tests for shot_name_builder.py."""

import os
import unittest

import render_job_to_rss
from protos import state_pb2
from utils_rr import path_utils


class TestRenderJobToRss(unittest.TestCase):
    """Tests for the ShotNameBuilder class."""

    def test_render_job_to_render_settings_setter(self) -> None:
        """Test that the shot name is built correctly."""
        self.maxDiff = None  # pylint: disable=invalid-name
        render_job = state_pb2.render_job()  # pylint: disable=no-member
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
        render_job.denoise = True
        render_job.scene = "Scene"
        render_job.view_layers.append("View Layer")
        render_job.comments = "This is a comment."
        settings = state_pb2.settings()  # pylint: disable=no-member
        rss = render_job_to_rss.render_job_to_render_settings_setter(
            render_job, settings
        )
        cwd = path_utils.normalize_drive_letter(os.getcwd())
        self.assertEqual(
            rss,
            (
                f"import sys ; sys.path.append('{cwd}') ; "
                "from utils_bpy import render_settings_setter ;"
                " rss = render_settings_setter.RenderSettingsSetter("
                "'Scene', ['View Layer']) ; rss.activate_addons([]) ; rss.set_camera('Camera') ; rss"
                ".set_render_settings(render_device='gpu', border=False, samples=128, motion_blur="
                "True, engine='cycles') ; rss.set_denoising_settings(denoise=True) ;"
                " rss.set_output_settings(frame_step=1, xres=1920, yres=1080, percres=100, "
                "high_quality=True) ; rss.custom_commands()"
            ),
        )
