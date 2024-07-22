"""Unit tests for shot_name_builder.py."""
import os
import pathlib
import tempfile
import unittest

import shot_name_builder
from protos import state_pb2


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
    render_job.file_format = "exr_single"
    render_job.engine = 0
    render_job.device = 0
    render_job.motion_blur = True
    render_job.overwrite = True
    render_job.high_quality = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    output_path = "/home/rob/Projects/renders/"
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(
        snb.frame_path, "/home/rob/Projects/renders/rr_test-hq-v01/rr_test-hq-v01-f####.exr")

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
    render_job.file_format = "png"
    render_job.engine = 0
    render_job.device = 0
    render_job.motion_blur = True
    render_job.overwrite = True
    render_job.high_quality = True
    render_job.denoise = True
    render_job.scene = "Scene"
    render_job.view_layers.append("View Layer")
    render_job.comments = "This is a comment."
    output_path = ""
    snb = shot_name_builder.ShotNameBuilder(render_job, output_path)
    self.assertEqual(
        snb.frame_path, "/home/rob/Projects/RenderRob/rr_test-hq-v01/rr_test-hq-v01-f####.png")

  def test_set_version_number(self):
    """Test set_version_number."""
    with tempfile.TemporaryDirectory() as tempdir:
      render_job = state_pb2.render_job()  # pylint:disable=no-member
      render_job.file = "/home/rob/Projects/RenderRob/rr_test.blend"
      render_job.active = True
      render_job.camera = "Camera"
      render_job.start = ""
      render_job.end = ""
      render_job.x_res = str(1920)
      render_job.y_res = str(1080)
      render_job.samples = str(128)
      render_job.file_format = "png"
      render_job.engine = 0
      render_job.device = 0
      render_job.motion_blur = True
      render_job.overwrite = False
      render_job.high_quality = True
      render_job.denoise = True
      render_job.scene = "Scene"
      render_job.view_layers.append("View Layer")
      render_job.comments = "This is a comment."

      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir)

      versionless_frame = os.path.join(
          tempdir, "rr_test-hq-v$$/rr_test-hq-v$$-f####.png").replace("\\", "/")

      # Empty folder leads to v01.
      render_job.overwrite = False
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v01/rr_test-hq-v01-f####.png").replace("\\", "/"))

      # Empty folder in replay mode leads to v01.
      render_job.overwrite = False
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v01/rr_test-hq-v01-f####.png").replace("\\", "/"))

      # Empty folder in overwrite mode leads to v01.
      render_job.overwrite = True
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v01/rr_test-hq-v01-f####.png").replace("\\", "/"))

      # v01 already exists, so v02 is returned.
      render_job.overwrite = False
      os.mkdir(os.path.join(tempdir, "rr_test-hq-v01"))
      with open(os.path.join(tempdir, "rr_test-hq-v01/rr_test-hq-v01-f0001.png"),
                'w', encoding="utf-8") as _:
        pass
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v02/rr_test-hq-v02-f####.png").replace("\\", "/"))

      # Replay mode, but v01 already exists, so v01 is returned.
      render_job.overwrite = False
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v01/rr_test-hq-v01-f####.png").replace("\\", "/"))

      # v01 and v02 already exist, but replay mode so v02 is returned.
      render_job.overwrite = False
      os.mkdir(os.path.join(tempdir, "rr_test-hq-v02"))
      with open(os.path.join(tempdir, "rr_test-hq-v02/rr_test-hq-v02-f0001.png"),
                'w', encoding="utf-8") as _:
        pass
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v02/rr_test-hq-v02-f####.png").replace("\\", "/"))

      # v01 and v02 already exist, so v03 is returned.
      render_job.overwrite = False
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v03/rr_test-hq-v03-f####.png").replace("\\", "/"))

      # Overwrite is set, so v02 is returned.
      render_job.overwrite = True
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v02/rr_test-hq-v02-f####.png").replace("\\", "/"))

      # Replay mode and overwrite is set, so v02 is returned.
      render_job.overwrite = True
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(versionless_frame), os.path.join(
          tempdir, "rr_test-hq-v02/rr_test-hq-v02-f####.png").replace("\\", "/"))

      # Still output folder is empty.
      render_job.overwrite = False
      render_job.start = "1"
      render_job.end = ""
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(os.path.join(tempdir,
                                                           "stills\\rr_test-hq-v$$-f####.png")),
                       os.path.join(tempdir, "stills", "rr_test-hq-v01-f####.png"
                                    ).replace("\\", "/"))

      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(os.path.join(tempdir,
                                                           "stills\\rr_test-hq-v$$-f####.png")),
                       os.path.join(tempdir, "stills", "rr_test-hq-v01-f####.png"
                                    ).replace("\\", "/"))

      # One image in still output folder.
      new_image = pathlib.Path(tempdir) / "stills/rr_test-hq-v01-f####.png"
      new_image.parent.mkdir(parents=True)
      new_image.touch()
      render_job.start = "1"
      render_job.end = ""
      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=False)
      self.assertEqual(snb.set_version_number(os.path.join(tempdir,
                                                           "stills\\rr_test-hq-v$$-f####.png")),
                       os.path.join(tempdir, "stills", "rr_test-hq-v02-f####.png"
                                    ).replace("\\", "/"))

      snb = shot_name_builder.ShotNameBuilder(render_job, tempdir, is_replay_mode=True)
      self.assertEqual(snb.set_version_number(os.path.join(tempdir,
                                                           "stills\\rr_test-hq-v$$-f####.png")),
                       os.path.join(tempdir, "stills", "rr_test-hq-v01-f####.png"
                                    ).replace("\\", "/"))


if __name__ == "__main__":
  unittest.main()
