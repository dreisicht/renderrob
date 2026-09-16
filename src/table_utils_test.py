"""Unit tests for table_utils.py."""

import unittest

from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QCheckBox

import main
from utils_rr import row_drag_table, table_utils

# The three rows every reorder test starts from, as (file, engine index, motion blur).
ROWS = (("job0.blend", 0, False), ("job1.blend", 1, True), ("job2.blend", 0, False))


class TestRowReordering(unittest.TestCase):
  """Tests for moving a row around, by the Up/Down buttons or by dragging it."""

  def setUp(self) -> None:
    """Build a main window holding three rows that can be told apart."""
    self.main_window = main.MainWindow()  # pylint:disable=no-member
    self.main_window.setup()
    # new_file is what leaves the table with one row that has all of its widgets; setup on its own
    # leaves the empty row the .ui file declares.
    self.main_window.new_file()
    self.table = self.main_window.table
    for _ in range(len(ROWS) - self.table.rowCount()):
      table_utils.add_row_below(self.table)
    for row, (file_name, engine, motion_blur) in enumerate(ROWS):
      self.table.item(row, 1).setText(file_name)
      self.table.cellWidget(row, 9).setCurrentIndex(engine)
      self.table.cellWidget(row, 11).findChild(QCheckBox).setChecked(motion_blur)
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests."""
    app_instance = QApplication.instance()
    app_instance.shutdown()
    del app_instance
    del self.main_window.app
    del self.main_window
    return super().tearDown()

  def rows(self) -> list[tuple[str, int, bool]]:
    """Read the table back in the shape of ROWS.

    A row is only really moved if its cell widgets come along, so the engine dropdown and the
    motion blur checkbox are part of what is compared.
    """
    return [
      (
        self.table.item(row, 1).text(),
        self.table.cellWidget(row, 9).currentIndex(),
        self.table.cellWidget(row, 11).findChild(QCheckBox).isChecked(),
      )
      for row in range(self.table.rowCount())
    ]

  def move_row(self, source_row: int, destination_row: int) -> None:
    """Move a row the way the main window does."""
    table_utils.move_row(
      self.table,
      source_row,
      destination_row,
      self.main_window.state_saver,
      self.main_window.before_table_change,
      self.main_window.after_table_change,
    )

  def test_setup_reads_back(self):
    """The fixture is only useful if the three rows can be told apart to begin with."""
    self.assertEqual(self.rows(), list(ROWS))

  def test_move_row_down(self):
    """A row dragged to the bottom takes its widget values with it."""
    self.move_row(0, 2)
    self.assertEqual(self.rows(), [ROWS[1], ROWS[2], ROWS[0]])

  def test_move_row_up(self):
    """A row dragged to the top ends up in front of the others."""
    self.move_row(2, 0)
    self.assertEqual(self.rows(), [ROWS[2], ROWS[0], ROWS[1]])

  def test_move_row_by_one(self):
    """Swapping two neighbours leaves the third row where it was."""
    self.move_row(1, 2)
    self.assertEqual(self.rows(), [ROWS[0], ROWS[2], ROWS[1]])

  def test_move_row_onto_itself_changes_nothing(self):
    """A row dropped where it already is must not even mark the file as unsaved."""
    self.main_window.is_saved = True
    self.move_row(1, 1)
    self.assertEqual(self.rows(), list(ROWS))
    self.assertTrue(self.main_window.is_saved)

  def test_move_row_clamps_out_of_range_destinations(self):
    """Dropping below the last row lands on it rather than past the end of the table."""
    self.move_row(0, self.table.rowCount())
    self.assertEqual(self.rows(), [ROWS[1], ROWS[2], ROWS[0]])

  def test_move_row_ignores_a_row_that_is_not_there(self):
    """A move without a selected row - currentRow is -1 then - is not a move."""
    self.move_row(-1, 0)
    self.assertEqual(self.rows(), list(ROWS))

  def test_moved_row_stays_current(self):
    """The moved row keeps the selection, so that Up or Down can be pressed again."""
    self.table.setCurrentCell(0, 2)
    self.move_row(0, 2)
    self.assertEqual((self.table.currentRow(), self.table.currentColumn()), (2, 2))

  def test_the_buttons_move_the_current_row(self):
    """The Up and the Down button move whichever row is selected."""
    self.table.setCurrentCell(2, 1)
    table_utils.move_row_up(
      self.table,
      self.main_window.state_saver,
      self.main_window.before_table_change,
      self.main_window.after_table_change,
    )
    self.assertEqual(self.rows(), [ROWS[0], ROWS[2], ROWS[1]])

    table_utils.move_row_down(
      self.table,
      self.main_window.state_saver,
      self.main_window.before_table_change,
      self.main_window.after_table_change,
    )
    self.assertEqual(self.rows(), list(ROWS))

  def test_the_half_of_a_row_decides_which_side_a_drop_lands_on(self):
    """A drop in the upper half of a row goes above it, one in the lower half below it."""
    self.table.resize(1400, 400)
    self.table.show()
    for row in range(self.table.rowCount()):
      top = self.table.rowViewportPosition(row)
      bottom = top + self.table.rowHeight(row) - 1
      self.assertEqual(row_drag_table.drop_row_at(self.table, top), row)
      self.assertEqual(row_drag_table.drop_row_at(self.table, bottom), row + 1)
    # Below the last row the table has nothing left to measure against, so a drop there goes to
    # the end rather than nowhere.
    self.assertEqual(row_drag_table.drop_row_at(self.table, 10000), self.table.rowCount())

  def test_the_insertion_line_is_drawn_between_the_rows(self):
    """The line marks the gap the row would drop into, not the cell under the cursor."""
    self.table.resize(1400, 400)
    self.table.show()
    self.assertEqual(
      row_drag_table.drop_indicator_y(self.table, 2),
      self.table.rowViewportPosition(2),
    )
    # Past the last row it closes the table off instead of running off the bottom of it.
    last_row = self.table.rowCount() - 1
    end_of_table = self.table.rowViewportPosition(last_row) + self.table.rowHeight(last_row)
    self.assertEqual(
      row_drag_table.drop_indicator_y(self.table, self.table.rowCount()),
      end_of_table,
    )

  def test_a_row_dragged_over_the_table_paints_the_insertion_line(self):
    """Painting the line must survive whichever palette Render Rob was started in."""
    self.table.resize(1400, 400)
    self.table.show()
    mime_data = QMimeData()
    mime_data.setData(row_drag_table.ROW_MIME_TYPE, b"0")
    self.table.dragMoveEvent(
      QDragMoveEvent(
        QPoint(10, self.table.rowViewportPosition(2)),
        Qt.MoveAction,
        mime_data,
        Qt.LeftButton,
        Qt.NoModifier,
      ),
    )
    self.table.viewport().grab()

  def test_a_dropped_blend_file_is_added_as_a_row(self):
    """Files dropped on the table still land in it, the way they did on the window alone."""
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("cube.blend")])
    self.table.dropEvent(
      QDropEvent(
        QPoint(10, 10),
        Qt.CopyAction,
        mime_data,
        Qt.LeftButton,
        Qt.NoModifier,
      ),
    )
    self.assertEqual(self.table.rowCount(), len(ROWS) + 1)
    self.assertEqual(self.table.item(self.table.rowCount() - 1, 1).text(), "cube.blend")

  def test_a_row_drop_reorders_the_table(self):
    """The drop the table reports has to arrive at the move as the main window wires it up.

    This walks the same path a real drag takes, minus the QDrag itself: that one spins an event
    loop of its own, which a test cannot drive.
    """
    self.table.resize(1400, 400)
    self.table.show()
    source_row = 0
    # Drop it in the lower half of the last row, which inserts it behind that row.
    drop_row = row_drag_table.drop_row_at(
      self.table,
      self.table.rowViewportPosition(2) + self.table.rowHeight(2) - 1,
    )
    self.table.rows_reordered.emit(
      source_row,
      row_drag_table.destination_for_drop(source_row, drop_row),
    )
    self.assertEqual(self.rows(), [ROWS[1], ROWS[2], ROWS[0]])


class TestDropPosition(unittest.TestCase):
  """Tests for turning a position in the table into the place a dragged row lands in."""

  def test_a_drop_in_front_of_the_first_row_goes_to_the_top(self):
    """Wherever the row came from, dropping it above the first one puts it first."""
    for source_row in range(4):
      self.assertEqual(row_drag_table.destination_for_drop(source_row, 0), 0)

  def test_destination_accounts_for_the_row_being_taken_out(self):
    """Everything below the dragged row moves up by one once the row has been taken out."""
    self.assertEqual(row_drag_table.destination_for_drop(0, 2), 1)
    self.assertEqual(row_drag_table.destination_for_drop(0, 3), 2)
    self.assertEqual(row_drag_table.destination_for_drop(2, 0), 0)
    self.assertEqual(row_drag_table.destination_for_drop(2, 1), 1)

  def test_dropping_a_row_next_to_itself_is_no_move(self):
    """Both edges of the dragged row lead back to where it already is."""
    self.assertEqual(row_drag_table.destination_for_drop(1, 1), 1)
    self.assertEqual(row_drag_table.destination_for_drop(1, 2), 1)


class TestDragFiltering(unittest.TestCase):
  """Tests that the table only takes the drags that are its own."""

  def setUp(self) -> None:
    """Build a table on its own - none of this needs the main window."""
    self.app = QApplication.instance() or QApplication([])
    self.table = row_drag_table.RowDragTableWidget()
    self.table.setColumnCount(2)
    self.table.setRowCount(2)
    return super().setUp()

  def tearDown(self) -> None:
    """Tear down the unit tests.

    The application has to go with them: Qt allows only one at a time, and the tests that build a
    whole main window bring their own.
    """
    del self.table
    self.app.shutdown()
    del self.app
    return super().tearDown()

  def drag_enter(self, mime_data: QMimeData) -> QDragEnterEvent:
    """Offer a drag to the table and hand the answered event back."""
    event = QDragEnterEvent(QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    self.table.dragEnterEvent(event)
    return event

  def test_a_row_drag_is_taken(self):
    """A drag carrying a row number is a reorder and belongs to the table."""
    mime_data = QMimeData()
    mime_data.setData(row_drag_table.ROW_MIME_TYPE, b"1")
    self.assertTrue(self.drag_enter(mime_data).isAccepted())

  def test_a_blend_file_drag_is_taken(self):
    """Dropped .blend files become rows, so the table has to take that drag too.

    Qt hands a drag to the innermost widget that accepts drops, so the table cannot leave those
    files to the window behind it the way it did before it took drops at all.
    """
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("cube.blend")])
    self.assertTrue(self.drag_enter(mime_data).isAccepted())

  def test_a_drag_without_a_blend_file_is_not_taken(self):
    """A drag that carries no .blend file is turned away at the table's edge.

    That is the same answer the window gives, and it is where the filtering happens: a drag that
    is let in because it carries a .blend brings whatever else was selected with it.
    """
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("notes.txt")])
    self.assertFalse(self.drag_enter(mime_data).isAccepted())

  def test_a_damaged_row_drag_is_not_taken(self):
    """A row number that is not a number is not a drag this table knows."""
    mime_data = QMimeData()
    mime_data.setData(row_drag_table.ROW_MIME_TYPE, b"not a row")
    self.assertEqual(row_drag_table.RowDragTableWidget.dragged_row(self.drag_enter(mime_data)), -1)


if __name__ == "__main__":
  unittest.main()
