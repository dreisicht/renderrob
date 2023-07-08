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
    rrs.settings.preview.nth_frame = 2
    rrs.settings.preview.resolution = 50
    rrs.render_jobs = [RenderJob()]
    ref_dict = {'render_jobs': [{'active': True,
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
                                 'y_res': ''}],
                'settings': Settings(blender_path='C:/Program Files '
                                     '(x86)/Steam/steamapps/common/Blender/blender.exe',
                                     output_path='test_data/output',
                                     blender_files_path='test_data/blender_files',
                                     preview=PreviewAttributes(samples=10,
                                                               nth_frame=2,
                                                               resolution=50))}
    self.assertEqual(rrs.to_dict(), ref_dict)


if __name__ == '__main__':
  unittest.main()
