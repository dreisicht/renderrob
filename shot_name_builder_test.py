"""Unit tests for shot_name_builder.py."""

import unittest
from proto import state_pb2
import shot_name_builder


class TestShotNameBuilder(unittest.TestCase):
  """Tests for the ShotNameBuilder class."""

  # def setUp(self) -> None:
  #   """Set up the test."""
  #   self.shot_name_builder = shot_name_builder.ShotNameBuilder()

  def test_get_shotname(self) -> None:
    """Test that the shot name is built correctly."""
    render_job = state_pb2.render_job()  # pylint:disable=no-member
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
    # render_job.animation_denoise = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    output_path = "/home"
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(snb.shotname, "rr_test-hq-v$$")

  def test_get_shotname_non_standard_names(self) -> None:
    """Test that the shot name is built correctly."""
    render_job = state_pb2.render_job()  # pylint:disable=no-member
    render_job.file = "/home/rob/Projects/RenderRob/rr_test.blend"
    render_job.active = True
    render_job.camera = "Camera.001"
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
    # render_job.animation_denoise = True
    render_job.denoise = True
    render_job.scene = "Scene.001"
    render_job.view_layers.append("View Layer")
    render_job.view_layers.append("View Layer.001")
    render_job.comments = "This is a comment."
    output_path = "/home"
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(snb.shotname, "rr_test-Cam.001-Sc.001-Vl+Vl.001-hq-v$$")

  def test_get_frame_path(self) -> None:
    """Test that the shot name is built correctly."""
    render_job = state_pb2.render_job()  # pylint:disable=no-member
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
    # render_job.animation_denoise = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    output_path = "/home/rob/Projects/renders/"
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(
        snb.frame_path, "/home/rob/Projects/renders/rr_test-hq-v01/rr_test-hq-v01-f####.png")

  def test_get_frame_path_no_output(self) -> None:
    """Test that the shot name is built correctly."""
    render_job = state_pb2.render_job()  # pylint:disable=no-member
    render_job.file = "/home/rob/Projects/RenderRob/rr_test.blend"
    render_job.active = True
    render_job.camera = "Camera"
    render_job.start = ""
    render_job.end = ""
    render_job.x_res = str(1920)
    render_job.y_res = str(1080)
    render_job.samples = str(128)
    render_job.file_format = 0
    render_job.engine = 0
    render_job.device = 0
    render_job.motion_blur = True
    render_job.overwrite = True
    render_job.high_quality = True
    # render_job.animation_denoise = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    output_path = ""
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(
        snb.frame_path, "/home/rob/Projects/RenderRob/stills/rr_test-hq-v01-f####.png")


if __name__ == "__main__":
  unittest.main()
