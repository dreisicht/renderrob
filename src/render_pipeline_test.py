"""End-to-end tests for the render pipeline: table -> Blender process -> frames on disk.

These start the real Blender binary, so they are skipped where none is installed - which includes
CI, where only the bpy wheel is available. Each render is kept tiny (64x48, one sample, CPU) so a
test takes about a second.
"""

import struct
import time
import unittest
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

import shot_name_builder
import test_support
from protos import state_pb2
from utils_rr import path_utils

BLENDER_PATH = path_utils.discover_blender_path()
RENDER_TIMEOUT_SECONDS = 120
WIDTH = 64
HEIGHT = 48


def read_png_size(png_path: Path) -> tuple[int, int]:
  """Read width and height from a PNG's IHDR chunk, without pulling in an image library."""
  header = png_path.read_bytes()[:24]
  return struct.unpack(">II", header[16:24])


@unittest.skipUnless(BLENDER_PATH, "No Blender binary found to render with.")
class TestRenderPipeline(unittest.TestCase):
  """Render jobs through the main window the way the Render button does."""

  def setUp(self) -> None:
    """Build a main window that renders the cube fixture into a throwaway folder."""
    self.main_window = test_support.make_main_window(self)
    self.output_dir = test_support.make_temp_dir(self)
    self.blend_file = test_support.copy_fixture(self, "cube.blend")
    settings = self.main_window.state_saver.state.settings
    settings.blender_path = BLENDER_PATH
    settings.output_path = str(self.output_dir)
    settings.blender_files_path = str(Path(self.blend_file).parent)
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests."""
    # Runs before the cleanups remove the temp folders a timed out render may still write into.
    self.kill_blender()
    app_instance = QApplication.instance()
    app_instance.shutdown()
    del app_instance
    del self.main_window.app
    del self.main_window
    return super().tearDown()

  def kill_blender(self) -> None:
    """Make sure a timed out render does not outlive the test."""
    process = self.main_window.process
    if process and process.state() != QProcess.NotRunning:
      process.kill()
      process.waitForFinished()

  def make_job(self, **fields: object) -> state_pb2.render_job:  # pylint: disable=no-member
    """Build a job that renders fast: CPU, one sample, a few pixels, an explicit frame range."""
    job = state_pb2.render_job(  # pylint: disable=no-member
      active=True,
      file=self.blend_file,
      camera="Camera",
      start="1",
      end="",
      x_res=str(WIDTH),
      y_res=str(HEIGHT),
      samples="1",
      file_format=state_pb2.file_format.png,
      engine=state_pb2.render_engine.cycles,
      # The proto default is gpu, which would go looking for OptiX.
      device=state_pb2.device.cpu,
      high_quality=True,
      scene="Scene",
      view_layers=["View Layer"],
    )
    for name, value in fields.items():
      setattr(job, name, value)
    return job

  def render(
    self,
    *jobs: state_pb2.render_job,  # pylint: disable=no-member
  ) -> list[state_pb2.render_job]:  # pylint: disable=no-member
    """Save the jobs to a file, open it, press Render and wait until the whole run is over.

    Returns the jobs the way the main window holds them afterwards. They went through the table,
    which writes the blend path relative to the Blender files folder.
    """
    # Going through a saved file is how the jobs reach the table in the app. It keeps the settings
    # made in setUp and by the test, since the state is copied rather than built afresh.
    file_state = state_pb2.render_rob_state()  # pylint: disable=no-member
    file_state.CopyFrom(self.main_window.state_saver.state)
    del file_state.render_jobs[:]
    file_state.render_jobs.extend(jobs)
    project_file = test_support.make_temp_dir(self) / "project.rrp"
    project_file.write_bytes(file_state.SerializeToString())
    self.main_window.open_file(str(project_file), ask_for_save=False)

    self.main_window.start_render()

    deadline = time.monotonic() + RENDER_TIMEOUT_SECONDS
    while not self.main_window.window.render_button.isEnabled():
      if time.monotonic() > deadline:
        self.fail(f"The render did not finish within {RENDER_TIMEOUT_SECONDS}s.")
      QApplication.processEvents()
      time.sleep(0.01)
    return list(self.main_window.state_saver.state.render_jobs)

  def frame_path(self, job: state_pb2.render_job, frame: int) -> Path:  # pylint: disable=no-member
    """Where the latest render of a frame is - the same lookup play_job does."""
    snb = shot_name_builder.ShotNameBuilder(job, self.output_dir, is_replay_mode=True)
    return Path(snb.frame_path.replace("####", str(frame).zfill(4)))

  def test_still(self) -> None:
    """A job with only a start frame renders that one frame into the stills folder."""
    (job,) = self.render(self.make_job(start="3"))

    self.assertEqual(list(self.main_window.green_jobs), [job])
    self.assertEqual(self.main_window.window.progressBar.value(), 100)
    expected = self.output_dir / "stills" / "cube-hq-v01-f0003.png"
    self.assertEqual(self.frame_path(job, 3), expected)
    self.assertEqual(sorted(path.name for path in expected.parent.iterdir()), [expected.name])

  def test_animation(self) -> None:
    """A job with a frame range renders every frame of it into its own shot folder."""
    (job,) = self.render(self.make_job(start="1", end="3"))

    self.assertEqual(list(self.main_window.green_jobs), [job])
    shot_dir = self.output_dir / "cube-hq-v01"
    self.assertEqual(
      sorted(path.name for path in shot_dir.iterdir()),
      [f"cube-hq-v01-f000{frame}.png" for frame in (1, 2, 3)],
    )
    for frame in (1, 2, 3):
      self.assertTrue(self.frame_path(job, frame).exists())

  def test_high_quality_uses_the_job_resolution(self) -> None:
    """The resolution in the table reaches Blender, overriding the 1920x1080 of the file."""
    (job,) = self.render(self.make_job())

    self.assertEqual(read_png_size(self.frame_path(job, 1)), (WIDTH, HEIGHT))

  def test_preview_applies_the_preview_settings(self) -> None:
    """A preview job renders at the preview resolution and skips frames by the preview step."""
    preview = self.main_window.state_saver.state.settings.preview
    preview.resolution = 50
    preview.resolution_use = True
    preview.frame_step = 2
    preview.frame_step_use = True
    (job,) = self.render(self.make_job(start="1", end="4", high_quality=False))

    shot_dir = self.output_dir / "cube-pv-v01"
    self.assertEqual(
      sorted(path.name for path in shot_dir.iterdir()),
      ["cube-pv-v01-f0001.png", "cube-pv-v01-f0003.png"],
    )
    self.assertEqual(read_png_size(self.frame_path(job, 1)), (WIDTH // 2, HEIGHT // 2))

  def test_several_jobs_skip_the_inactive_ones(self) -> None:
    """Every active job renders in turn, and an inactive one is left alone."""
    still, inactive, animation = self.render(
      self.make_job(start="1"),
      self.make_job(start="5", active=False),
      self.make_job(start="1", end="2", high_quality=False),
    )

    self.assertEqual(list(self.main_window.green_jobs), [still, animation])
    self.assertNotIn(inactive, self.main_window.yellow_jobs)
    self.assertNotIn(inactive, self.main_window.red_jobs)
    self.assertTrue(self.frame_path(still, 1).exists())
    self.assertTrue(self.frame_path(animation, 2).exists())
    self.assertFalse(self.frame_path(inactive, 5).exists())

  def test_rendering_again_creates_a_new_version(self) -> None:
    """Without overwrite, a second render goes into the next version instead of replacing."""
    job = self.make_job(start="1", end="1")

    self.render(job)
    self.render(job)

    self.assertTrue((self.output_dir / "cube-hq-v01" / "cube-hq-v01-f0001.png").exists())
    self.assertTrue((self.output_dir / "cube-hq-v02" / "cube-hq-v02-f0001.png").exists())

  def test_overwrite_keeps_the_version(self) -> None:
    """With overwrite, a second render goes back into the version it rendered before."""
    job = self.make_job(start="1", end="1", overwrite=True)

    self.render(job)
    self.render(job)

    self.assertEqual(
      sorted(path.name for path in self.output_dir.iterdir()),
      ["cube-hq-v01"],
    )

  def test_relative_blend_path(self) -> None:
    """A path relative to the Blender files folder is resolved before Blender is started."""
    job = self.make_job(file=Path(self.blend_file).name)

    self.render(job)

    self.assertTrue((self.output_dir / "stills" / "cube-hq-v01-f0001.png").exists())


if __name__ == "__main__":
  unittest.main()
