"""Integration tests for the solution class."""
import unittest

from render_job import RenderJob
from render_rob_state import PreviewAttributes, RenderRobState, Settings


class TestRenderRobState(unittest.TestCase):
  """Unit test for roman to integer."""

  def test_open_from_json(self):
    """Test opening from JSON."""
    state = RenderRobState()
    state.open_from_json("test_data/state.json")
    self.assertEqual(state.settings["blender_path"],
                     "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe")

  def test_to_table(self):
    """Test to table."""
    # TODO(b/296): Find a good way to test QT UIs.

  def test_to_dict(self):
    """Test to dict."""
    self.maxDiff = None  # pylint: disable=invalid-name
    rrs = RenderRobState()
    rrs.settings.blender_path = "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe"
    rrs.settings.output_path = "test_data/output"
    rrs.settings.blender_files_path = "test_data/blender_files"
    rrs.settings.addons_to_activate = ["test_data/addon1.py", "test_data/addon2.py"]
    rrs.settings.preview.samples = 10
    rrs.settings.preview.samples_use = True
    rrs.settings.preview.nth_frame = 2
    rrs.settings.preview.nth_frame_use = True
    rrs.settings.preview.resolution = 50
    rrs.settings.preview.resolution_use = True
    rrs.render_jobs = [RenderJob()]
    ref_dict = {'settings': Settings(blender_path='C:/Program Files '
                                     '(x86)/Steam/steamapps/common/Blender/blender.exe',
                                     output_path='test_data/output',
                                     blender_files_path='test_data/blender_files',
                                     preview=PreviewAttributes(samples=10,
                                                               samples_use=True,
                                                               nth_frame=2,
                                                               nth_frame_use=True,
                                                               resolution=50,
                                                               resolution_use=True).__dict__).__dict__,
                'render_jobs': [{'active': True,
                                 'animation_denoise': False,
                                 'camera': '',
                                 'comments': '',
                                 'denoise': False,
                                 'device': '',
                                 'end': '',
                                 'engine': '',
                                 'file': '',
                                 'file_format': '',
                                 'high_quality': False,
                                 'motion_blur': False,
                                 'new_version': False,
                                 'samples': '',
                                 'scene': '',
                                 'start': '',
                                 'view_layer': '',
                                 'x_res': '',
                                 'y_res': ''}]}
    self.assertCountEqual(rrs.to_dict(), ref_dict)  # TODO: Is this the right assertion?


if __name__ == '__main__':
  unittest.main()
