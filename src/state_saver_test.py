"""Test the state_saver module."""
import unittest

from PySide6.QtWidgets import QApplication

import main
import state_saver
from protos import state_pb2
from utils_rr import table_utils


class TestStateSaver(unittest.TestCase):
  """Test the state_saver module."""

  def setUp(self) -> None:
    """Set up the unit tests."""
    self.main_window = main.MainWindow()  # pylint:disable=no-member
    self.main_window.setup()
    table_utils.add_row_below(self.main_window.table)
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests."""
    app_instance = QApplication.instance()
    app_instance.shutdown()
    del app_instance
    del self.main_window.app
    del self.main_window
    return super().tearDown()

  def test_get_text(self):
    """Test the get_text method."""
    self.assertEqual(state_saver.get_text(self.main_window.table.cellWidget(0, 2)), "")
    self.assertTrue(state_saver.get_text(
        self.main_window.table.cellWidget(0, 0), widget="checkbox"))
    self.assertEqual(state_saver.get_text(
        self.main_window.table.cellWidget(0, 8), widget="dropdown"), "exr_single")

  def test_state_to_table(self):
    """Test the state_to_table method."""
    state_saver_instance = state_saver.StateSaver()
    with open("test/basic_state.rrp", "rb") as rrp_file:
      state_saver_instance.state.ParseFromString(rrp_file.read())

    table = self.main_window.table
    state_saver_instance.state_to_table(table)
    self.assertEqual(table.rowCount(), 1)
    self.assertEqual(table.columnCount(), 18)
    self.assertTrue(state_saver.get_text(table.cellWidget(0, 0), widget="checkbox"))
    self.assertEqual(state_saver.get_text(table.item(0, 1)), "test/cube.blend")
    self.assertEqual(state_saver.get_text(table.item(0, 2)), "b")
    self.assertEqual(state_saver.get_text(table.item(0, 3)), "1")
    self.assertEqual(state_saver.get_text(table.item(0, 4)), "2")
    self.assertEqual(state_saver.get_text(table.item(0, 5)), "3")
    self.assertEqual(state_saver.get_text(table.item(0, 6)), "4")
    self.assertEqual(state_saver.get_text(table.item(0, 7)), "5")
    self.assertEqual(state_saver.get_text(table.cellWidget(0, 8), widget="dropdown"), "exr_single")
    self.assertEqual(state_saver.get_text(table.cellWidget(0, 9), widget="dropdown"), "cycles")
    self.assertEqual(state_saver.get_text(table.cellWidget(0, 10), widget="dropdown"), "gpu")
    self.assertTrue(state_saver.get_text(table.cellWidget(0, 11), widget="checkbox"))
    self.assertFalse(state_saver.get_text(table.cellWidget(0, 12), widget="checkbox"))
    self.assertTrue(state_saver.get_text(table.cellWidget(0, 13), widget="checkbox"))
    self.assertFalse(state_saver.get_text(table.cellWidget(0, 14), widget="checkbox"))
    self.assertEqual(state_saver.get_text(table.item(0, 15)), "c")
    self.assertEqual(state_saver.get_text(table.item(0, 16)).split(";"), ["d"])
    self.assertEqual(state_saver.get_text(table.item(0, 17)), "e")

  def test_table_to_state(self):
    """Test the table_to_state method."""
    self.main_window.open_file("test/basic_state.rrp")
    state_saver_instance = state_saver.StateSaver()
    state_saver_instance.parent_widget = self.main_window
    state_saver_instance.table_to_state(self.main_window.table)
    reference_state = state_pb2.render_rob_state()  # pylint: disable=no-member
    with open("test/basic_state.rrp", "rb") as rrp_file:
      reference_state.ParseFromString(rrp_file.read())
    self.assertEqual(state_saver_instance.state.render_jobs, reference_state.render_jobs)
