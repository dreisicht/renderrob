"""Unit tests for main module."""

import unittest
from pathlib import Path

from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QApplication

import main
from utils_rr import table_utils, ui_utils

# pylint: disable=protected-access

# Test fixtures live next to the repository root, so resolve them relative to this file rather
# than to the current working directory.
SAVE_FILE = str(Path(__file__).parent.parent / "test" / "test_save_file.rrp")


class TestMainWindow(unittest.TestCase):
  """Unit tests for MainWindow."""

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

  def test_add_filepath_to_cache(self):
    """Test the add_filepath_to_cache function."""
    self.main_window.add_filepath_to_cache(SAVE_FILE)
    self.assertIn(SAVE_FILE, self.main_window.cache.recent_files)

  def test_new_file(self):
    """Test the new_file function."""
    self.main_window.new_file()

  def test_open_file(self):
    """Test the open_file function."""
    filepath = SAVE_FILE
    self.main_window.open_file(filepath)
    self.assertTrue(filepath in self.main_window.cache.current_file)
    self.assertEqual(self.main_window.cache.current_file, filepath)

  def test_quit(self):
    """Test the quit function."""
    self.main_window.quit()

  def test_row_context_menu_mirrors_the_buttons(self):
    """The row context menu offers every button beside the table, plus the cell operators."""
    index = self.main_window.table.model().index(0, 1)
    menu = self.main_window.build_row_context_menu(index)

    labels = [action.text() for action in menu.actions() if not action.isSeparator()]
    for button_name in main.ROW_CONTEXT_MENU_BUTTONS:
      if button_name is None:
        continue
      tooltip = getattr(self.main_window.window, button_name).toolTip()
      self.assertTrue(
        any(label.startswith(tooltip) for label in labels),
        f"{button_name} is missing from the context menu",
      )
    self.assertIn("Copy cell", labels)
    self.assertIn("Paste cell", labels)

  def test_row_context_menu_skips_cell_operators_on_widget_cells(self):
    """A checkbox cell has no text to copy, so the menu leaves the cell operators out."""
    index = self.main_window.table.model().index(0, 0)
    menu = self.main_window.build_row_context_menu(index)

    labels = [action.text() for action in menu.actions() if not action.isSeparator()]
    self.assertNotIn("Copy cell", labels)
    self.assertNotIn("Paste cell", labels)

  def test_dropdown_cells_forward_their_right_clicks(self):
    """A QComboBox keeps the context menu event to itself, so the cell has to forward it by hand.

    Without the forwarding the three dropdown columns are dead to right-clicks, while every other
    kind of cell propagates to the table on its own.
    """
    table = self.main_window.table
    table.resize(1400, 400)
    table.show()
    # The real handler opens a menu and waits for it, which would hang the test.
    table.customContextMenuRequested.disconnect(self.main_window.show_row_context_menu)
    positions = []
    table.customContextMenuRequested.connect(positions.append)

    for column in ui_utils.COMBOBOX_COLUMNS:
      index = table.model().index(0, column)
      dropdown = table.cellWidget(0, column)
      # Put the dropdown where the table would put it. What is under test is the forwarding, and
      # a table that has not been painted yet is free to place its cell widgets later.
      dropdown.setGeometry(table.visualRect(index))
      centre = dropdown.rect().center()
      QApplication.sendEvent(
        dropdown,
        QContextMenuEvent(QContextMenuEvent.Mouse, centre, dropdown.mapToGlobal(centre)),
      )

      self.assertTrue(positions, f"the dropdown in column {column} swallowed the right-click")
      forwarded = table.indexAt(positions[-1])
      self.assertEqual((forwarded.row(), forwarded.column()), (0, column))

  def test_row_context_menu_position_is_viewport_relative(self):
    """The position the table hands over addresses the viewport, not the table.

    Mapping it through the table instead would miss by the height of the header.
    """
    table = self.main_window.table
    table.resize(1400, 400)
    index = table.model().index(0, 1)

    position = table.visualRect(index).center()
    self.assertEqual(table.indexAt(position).row(), index.row())
    self.assertEqual(table.indexAt(position).column(), index.column())


if __name__ == "__main__":
  unittest.main()
