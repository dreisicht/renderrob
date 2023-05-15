"""Tests the functionalities in the GSpread."""
from unittest import TestCase

from google.oauth2.credentials import Credentials

import rr_gspread


class TestGspread(TestCase):
  """Tests the functionalities in the GSpread."""

  def test_authorize_user(self) -> None:
    """Tests the authorize_user function."""
    self.assertEqual(type(rr_gspread.authorize_user()), Credentials)

  def test_query_sheet(self) -> None:
    """Tests the query_sheet function."""
    expected_result = ([['', 'active', '.blend file path', 'active camera', 'start\nframe', 'end\nframe', 'X\nres', 'Y\nres', 'samples', 'file\nformat', 'Cycles\n(Eevee)', 'CPU', 'GPU', 'motion\nblur', 'new\nversion', 'high\nquality', 'anima-\ntion\ndenoise', 'denoise', 'scene', 'view layer', 'comments'],
                        ['', 'TRUE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', '', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE',
                         'TRUE', 'FALSE', 'FALSE', '', '', '', 'TRUEfile.blendCamera12501920108016exrTRUETRUETRUETRUETRUETRUEFALSEFALSE'],
                        ['', 'FALSE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', 'exr', 'TRUE',
                         'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'FALSE', 'FALSE', '', '', '', '#REF!'],
                        ['', 'FALSE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', 'exr', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'FALSE', 'FALSE', '', '', '',
                         'FALSEfile.blendCamera12501920108016exrTRUETRUETRUETRUETRUETRUEFALSEFALSE'],
                        ['', 'FALSE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', 'exr', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE',
                         'TRUE', 'FALSE', 'FALSE', '', '', '', 'FALSEfile.blendCamera12501920108016exrTRUETRUETRUETRUETRUETRUEFALSEFALSE'],
                        ['', 'FALSE', 'file.blend', 'Camera', '1', '250', '1920', '1080', '16', 'exr', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'FALSE', 'FALSE', '', '', '', 'FALSEfile.blendCamera12501920108016exrTRUETRUETRUETRUETRUETRUEFALSEFALSE']],
                       [['path to blender', 'C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe'],
                        ['path to render output folder', 'C:\\Path\\To\\My\\Renders'],
                        ['path to blender files folder', '"C:\\Users\\peter\\Desktop\\opt"'],
                        ['preview resolution in %', '25', 'TRUE'],
                        ['preview samples', '1', 'TRUE'],
                        ['preview n-th frames', '24', 'FALSE'],
                        ['addons to activate']])
    self.assertEqual(expected_result,
                     rr_gspread.download_spreadsheet_content())
