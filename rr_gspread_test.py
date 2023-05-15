"""Tests the functionalities in the GSpread."""
import os
from unittest import TestCase

import googleapiclient

import rr_gspread


class TestGspread(TestCase):
  """Tests the functionalities in the GSpread."""

  def setUp(self) -> None:
    os.chdir("src")

    return super().setUp()

  def test_get_authenticated_service(self) -> None:
    """Tests the get_authenticated_service function."""
    a = rr_gspread.get_authenticated_service()
    self.assertEqual(type(rr_gspread.get_authenticated_service()), googleapiclient.discovery.Resource)

  def test_query_sheet(self) -> None:
    """Tests the query_sheet function."""
    expected_result = ([['', 'active', '.blend file path', 'active camera', 'start\nframe', 'end\nframe', 'X\nres', 'Y\nres', 'samples', 'file\nformat', 'Cycles\n(Eevee)', 'CPU', 'GPU', 'motion\nblur', 'new\nversion', 'high\nquality', 'anima-\ntion\ndenoise', 'denoise', 'scene', 'view layer', 'comments'],
                        ['', 'TRUE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', '', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE',
                         'TRUE', 'FALSE', 'FALSE', '', '', '', 'TRUEfile.blendCamera12501920108016TRUETRUETRUETRUETRUETRUEFALSEFALSE'],
                        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '#REF!']],
                       [['path to blender', 'C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe'],
                        ['path to render output folder', 'C:\\Path\\To\\My\\Renders'],
                        ['path to blender files folder', '"C:\\Users\\peter\\Desktop\\opt"'],
                        ['preview resolution in %', '25', 'TRUE'],
                        ['preview samples', '1', 'TRUE'],
                        ['preview n-th frames', '24', 'FALSE'],
                        ['addons to activate']])
    self.assertEqual(expected_result,
                     rr_gspread.query_sheet(spreadsheet_id="1RK9LehhMt0vEDU9_usjELTvF397WePwqncWAU5hL94A"))
