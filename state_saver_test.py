"""Test the state_saver module."""
import state_saver

import unittest
import renderrob  # type: ignore
from utils import table_utils
# TODO: Where do I get a QTableWidget from?


class TestStateSaver(unittest.TestCase):
  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = renderrob.MainWindow()
    self.app = self.main_window.setup()
    table_utils.add_row_below()
    return super().setUp()

  def test_get_text(self):
    self.assertEqual(state_saver.get_text(
        self.main_window.table.cellWidget(0, 2)), "")
    self.assertTrue(state_saver.get_text(
        self.main_window.table.cellWidget(0, 0), widget="checkbox"))
    self.assertEqual(state_saver.get_text(
        self.main_window.table.cellWidget(0, 8), widget="dropdown"), "png")

  def test_state_to_table(self):
    pass

  def test_table_to_state(self):
    pass
