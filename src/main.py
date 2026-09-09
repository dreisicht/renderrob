"""Main file to open RenderRob."""

import os
import platform
import subprocess
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent.as_posix())
sys.path.append(Path(__file__).parent.parent.as_posix())


from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor, QIcon, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
  QApplication,
  QFileDialog,
  QMessageBox,
  QStackedLayout,
  QTableWidgetItem,
  QWidget,
)

import settings_window
import shot_name_builder
import state_saver
from protos import cache_pb2, state_pb2
from render_job_to_rss import render_job_to_render_settings_setter
from utils_common import print_utils
from utils_rr import path_utils, placeholder_delegate, table_utils, ui_utils
from utils_rr.dropwidget import DropWidget

MAX_NUMBER_OF_RECENT_FILES = 5

UI_FILE_NAME = "window.ui"

# Qt reports the color scheme as an enum whose values are Unknown/Light/Dark.
LIGHT_COLOR_SCHEME = 1
DARK_COLOR_SCHEME = 2

# How far from the bottom of the console the user may be and still have the view follow the output.
CONSOLE_FOLLOW_THRESHOLD = 1500

# Exit codes Render Rob reads back from a finished Blender run. 987 is Render Rob's own code for
# "the job produced warnings"; 62097 is the one print_utils.print_error exits with.
SUCCESS_EXIT_CODES = (0, 1)
WARNING_EXIT_CODE = 987
FAILURE_EXIT_CODES = (62097, 11)


class MainWindow(QWidget):
  """Main window for RenderRob."""

  ########### SETUP ############

  def get_temp_dir(self) -> Path:
    """Get the temporary directory for cache files."""
    if sys.platform == "darwin":
      temp_dir = Path(os.getenv("TMPDIR"))
    else:
      temp_dir = Path.cwd()
    if not temp_dir.exists():
      temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.app = QApplication(sys.argv)
    super().__init__()
    self.window = None
    self.table = None
    self.cache = cache_pb2.RenderRobCache()  # pylint: disable=no-member
    self.state_saver = state_saver.StateSaver()

    self.recent_file_actions = None
    self.process = None
    self.is_saved = True
    self.recent_states = []

    self.active_render_job = None
    self.green_jobs = []
    self.yellow_jobs = []
    self.red_jobs = []

    self.cache_path = self.get_temp_dir() / ".rr_cache"

    # NOTE: Avoid global state with theme colors.
    if self.app.styleHints().colorScheme().value == LIGHT_COLOR_SCHEME:
      table_utils.COLORS = table_utils.COLORS_LIGHT
    elif self.app.styleHints().colorScheme().value == DARK_COLOR_SCHEME:
      table_utils.COLORS = table_utils.COLORS_DARK

  def setup(self) -> None:
    """Provide main function."""
    self.app.setStyle("Breeze")
    if self.cache_path.exists():
      self.load_cache()
    self.resize(1800, self.app.primaryScreen().size().height())
    self.window = ui_utils.load_ui_from_file(UI_FILE_NAME, custom_widgets=[DropWidget])
    self.window.splitter.setSizes((200, 500))

    self.window.setWindowIcon(QIcon("icon/icon-256.png"))
    self.app.setWindowIcon(QIcon("icon/icon-256.png"))
    self.table = self.window.tableWidget
    self.table.setStyleSheet(
      "QTableWidget {background-color: " + str(table_utils.COLORS["grey_light"]) + "}",
    )
    self.refresh_recent_files_menu()
    self.window.progressBar.setValue(0)
    self.window.progressBar.setMinimum(0)
    self.window.progressBar.setMaximum(100)
    layout = QStackedLayout()
    layout.addWidget(self.window)
    self.setLayout(layout)
    self.make_main_window_connections()
    placeholder_delegate.setup_placeholder_delegate(self.table)

  def execute(self) -> None:
    """Execute the main window.

    NOTE: For unit testing, this function should not be called.
    """
    self.setup()
    self.new_file()
    self.save_cache()
    self.show()
    self.app.exec()

  ############### EVENTS ###############
  def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
    """Handle the close event."""
    if self.is_saved:
      event.accept()
      return
    reply = QMessageBox.question(
      self,
      "Message",
      "Save changes?",
      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
      QMessageBox.Cancel,
    )

    if reply == QMessageBox.Yes:
      self.save_file()
      event.accept()
    elif reply == QMessageBox.No:
      event.accept()
    elif reply == QMessageBox.Cancel:
      event.ignore()

  def quit(self) -> None:
    """Quit the application."""
    self.save_cache()
    QCoreApplication.quit()

  def make_main_window_connections(self) -> None:
    """Make connections for buttons."""
    self.window.add_button.clicked.connect(
      lambda: table_utils.add_row_below(
        self.table,
        self.before_table_change,
        self.after_table_change,
      ),
    )
    self.window.delete_button.clicked.connect(
      lambda: table_utils.remove_active_row(
        self.table,
        self.before_table_change,
        self.after_table_change,
      ),
    )
    self.window.play_button.clicked.connect(self.play_job)
    self.window.open_button.clicked.connect(self.open_output_folder)
    self.window.up_button.clicked.connect(
      lambda: table_utils.move_row_up(
        self.table,
        self.before_table_change,
        self.after_table_change,
      ),
    )
    self.window.down_button.clicked.connect(
      lambda: table_utils.move_row_down(
        self.table,
        self.before_table_change,
        self.after_table_change,
      ),
    )

    self.window.actionCopy_cell.triggered.connect(self.copy_from_cell)
    self.window.actionPaste_cell.triggered.connect(self.paste_into_cell)

    self.window.render_button.clicked.connect(self.start_render)
    self.window.stop_button.clicked.connect(self.stop_render)
    self.window.actionOpen.triggered.connect(self.open_file_dialog)
    self.window.actionSave.triggered.connect(self.save_file)
    self.window.actionSave_As.triggered.connect(self.save_as_file)
    self.window.actionSettings.triggered.connect(self.open_settings_window)
    self.window.actionNew.triggered.connect(self.new_file)
    self.window.actionQuit.triggered.connect(self.quit)
    self.table.itemChanged.connect(self.before_and_after_table_change)
    self.window.blender_button.clicked.connect(self.open_blender_file)
    self.window.duplicate_button.clicked.connect(
      lambda: table_utils.duplicate_row(
        self.table,
        self.state_saver,
        self.before_table_change,
        self.after_table_change,
      ),
    )
    self.window.actionUndo.triggered.connect(self.undo)
    self.window.sync_button.clicked.connect(self.load_settings_from_blender)
    ui_utils.TABLE_CHANGED_FUNCTION = self.before_and_after_table_change

  ######## CACHE UTILS ##########
  def save_cache(self) -> None:
    """Store the cache to a file."""
    self.cache_path.write_bytes(self.cache.SerializeToString())

  def load_cache(self) -> None:
    """Load the cache from a file."""
    self.cache.current_file = ""
    self.cache.ParseFromString(self.cache_path.read_bytes())

  def add_filepath_to_cache(self, file_name: str) -> None:
    """Add a filepath to the cache."""
    if file_name not in self.cache.recent_files:
      self.cache.recent_files.insert(0, file_name)
      if len(self.cache.recent_files) > MAX_NUMBER_OF_RECENT_FILES:
        self.cache.recent_files.pop()

  def save_as_file(self) -> None:
    """Save the state to a serialized proto file with a dialog."""
    self.state_saver.table_to_state(self.table)
    file_name, _ = QFileDialog.getSaveFileName(
      self.window,
      "Save File",
      "",
      "Render Rob Files (*.rrp)",
    )
    Path(file_name).write_bytes(self.state_saver.state.SerializeToString())
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.refresh_recent_files_menu()
    self.is_saved = True
    self.window.parent().setWindowTitle("Render Rob " + self.cache.current_file)

  def save_file(self) -> None:
    """Save the state to a serialized proto file without a dialog."""
    self.state_saver.table_to_state(self.table)
    Path(self.cache.current_file).write_bytes(self.state_saver.state.SerializeToString())
    self.is_saved = True
    self.window.parent().setWindowTitle("Render Rob " + self.cache.current_file)

  def new_file(self) -> None:
    """Create a new file."""
    self.window.parent().setWindowTitle("* Render Rob")
    if not self.ask_for_save():
      return
    for _ in range(self.table.rowCount()):
      self.table.removeRow(0)
    self.cache.current_file = ""
    self.state_saver.state.FromString(b"")
    self.state_saver.parent_widget = self
    self.recent_states = [b""]
    self.window.render_button.setEnabled(True)
    self.window.stop_button.setEnabled(False)
    table_utils.post_process_row(self.table, 0)
    table_utils.add_row_below(self.table)

  def clear_recent_files(self) -> None:
    """Clear the recent files."""
    del self.cache.recent_files[:]
    self.window.menuOpen_Recent.clear()
    self.recent_file_actions = []

  def refresh_recent_files_menu(self) -> None:
    """Add the recent files to the file menu."""
    self.window.menuOpen_Recent.clear()
    open_recent_functions = [
      lambda: self.open_file(self.cache.recent_files[0]),
      lambda: self.open_file(self.cache.recent_files[1]),
      lambda: self.open_file(self.cache.recent_files[2]),
      lambda: self.open_file(self.cache.recent_files[3]),
      lambda: self.open_file(self.cache.recent_files[4]),
    ]
    for i, file_path in enumerate(self.cache.recent_files):
      action_recent = QAction(Path(file_path).name, self.window.menuOpen_Recent)
      action_recent.triggered.connect(open_recent_functions[i])
      self.window.menuOpen_Recent.addAction(action_recent)

    self.window.menuOpen_Recent.addSeparator()
    if self.cache.recent_files:
      action_clear = QAction("Clear Recent Files", self.window.menuOpen_Recent)
      action_clear.triggered.connect(self.clear_recent_files)
      self.window.menuOpen_Recent.addAction(action_clear)
    self.save_cache()

  def open_file_dialog(self) -> None:
    """Open a RenderRob file with a dialog."""
    if not self.ask_for_save():
      return
    file_name, _ = QFileDialog.getOpenFileName(
      self.window,
      "Open File",
      "",
      "RenderRob Files (*.rrp)",
    )
    self.open_file(file_name, ask_for_save=False)

  def open_file(self, file_name: str, *, ask_for_save: bool = True) -> None:
    """Open a RenderRob file."""
    self.green_jobs = []
    self.yellow_jobs = []
    self.red_jobs = []
    if ask_for_save and not self.ask_for_save():
      return
    if file_name == "":
      return
    self.table.blockSignals(True)
    self.state_saver.state.ParseFromString(Path(file_name).read_bytes())
    self.state_saver.state_to_table(self.table)
    self.cache.current_file = file_name
    self.window.parent().setWindowTitle("Render Rob " + file_name)
    self.add_filepath_to_cache(file_name)
    self.cache.recent_files.remove(file_name)
    self.cache.recent_files.insert(0, file_name)
    self.refresh_recent_files_menu()
    self.recent_states = [self.state_saver.state.SerializeToString()]
    self.after_table_change()
    self.table.blockSignals(False)

  def ask_for_save(self) -> bool:
    """Ask the user to save the current file. Returns True if the user wants to continue."""
    if self.is_saved:
      return True
    reply = QMessageBox.question(
      self,
      "Message",
      "Save changes?",
      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
      QMessageBox.Cancel,
    )
    if reply == QMessageBox.Yes:
      self.save_file()
      return True
    if reply == QMessageBox.No:
      return True
    if reply == QMessageBox.Cancel:
      return False
    return None

  ######### CONSOLE WINDOW ###########
  def _scroll_console_to_end_if_at_bottom(self) -> None:
    """Follow the output, but only while the user has not scrolled up to read something."""
    scroll_bar = self.window.textBrowser.verticalScrollBar()
    if scroll_bar.value() > scroll_bar.maximum() - CONSOLE_FOLLOW_THRESHOLD:
      self.window.textBrowser.moveCursor(QTextCursor.End)

  def _color_active_job_row(self, color_name: str) -> None:
    """Color the row of the job that is currently rendering."""
    self.state_saver.table_to_state(self.table)
    row_number = state_saver.find_job(
      self.state_saver.state.render_jobs,
      self.active_render_job,
    )
    table_utils.color_row_background(self.table, row_number, QColor(table_utils.COLORS[color_name]))

  def _classify_console_line(self, line: str) -> tuple[str, QTextCharFormat]:
    """Strip Render Rob's ANSI markers off a line and return the format to render it with.

    print_utils prefixes Render Rob's own messages with a background/foreground pair. A warning
    or an error also colors the row of the job that produced it.
    """
    bash_colors = print_utils.BASH_COLORS
    # (ANSI prefix, text background, text foreground, row color)
    severities = (
      (bash_colors["BACK_RED"] + " " + bash_colors["FORE_WHITE"], "red", "white", "red"),
      (
        bash_colors["BACK_YELLOW"] + " " + bash_colors["FORE_BLACK"],
        "yellow",
        "black_dark",
        "yellow",
      ),
      (
        bash_colors["BACK_CYAN"] + " " + bash_colors["FORE_BLACK"],
        "blue_grey_lighter",
        "black_dark",
        None,
      ),
    )

    color_format = QTextCharFormat()
    color_format.setBackground(QColor(table_utils.COLORS["console_background"]))
    color_format.setForeground(QColor(table_utils.COLORS["console_foreground"]))

    # A crash report is an error, even though Blender does not mark it up as one.
    is_crash = "blender.crash.txt" in line
    for prefix, background, foreground, row_color in severities:
      if not line.startswith(prefix) and not (is_crash and row_color == "red"):
        continue
      line = line.replace(prefix, "")
      color_format.setBackground(QColor(table_utils.COLORS[background]))
      color_format.setForeground(QColor(table_utils.COLORS[foreground]))
      if row_color:
        self._color_active_job_row(row_color)
      break

    return line.replace(bash_colors["RESET_ALL"], ""), color_format

  def _handle_output(self) -> None:
    """Output the subprocess output to the textbrowser widget."""
    self.table.blockSignals(True)
    output = self.process.readAll().data().decode()

    if "\u001b" in output:
      for line in output.splitlines():
        text, color_format = self._classify_console_line(line)
        self._scroll_console_to_end_if_at_bottom()
        self.window.textBrowser.setCurrentCharFormat(color_format)
        self.window.textBrowser.insertPlainText(text + "\n")
    else:
      self._scroll_console_to_end_if_at_bottom()
      self.window.textBrowser.setCurrentCharFormat(QTextCharFormat())
      self.window.textBrowser.insertPlainText(output)

    # Always show the end of the run, whether it finished or crashed.
    if "Blender quit" in output or "blender.crash.txt" in output:
      self.window.textBrowser.moveCursor(QTextCursor.End)

    self.table.blockSignals(False)

  ##### STATE OPS #####
  def undo(self) -> None:
    """Undo the last action."""
    if not self.recent_states:
      return
    self.state_saver.state.ParseFromString(self.recent_states.pop())
    # Refactor: The blockSignals could be done as a context manager on the top level operator
    # methods.
    self.table.blockSignals(True)
    self.state_saver.state_to_table(self.table)
    self.table.blockSignals(False)

  def before_table_change(self) -> None:
    """Handle before table change."""
    self.is_saved = False
    self.window.parent().setWindowTitle("* Render Rob" + self.cache.current_file)

    self.state_saver.table_to_state(self.table)
    state_string = self.state_saver.state.SerializeToString()
    if not self.recent_states or self.recent_states[-1] != state_string:
      self.recent_states.append(state_string)

  def after_table_change(self, item: QTableWidgetItem | None = None) -> None:
    """Handle after table change."""
    self.state_saver.table_to_state(self.table)
    if item and isinstance(item, QTableWidgetItem) and item.column() == 1:
      table_utils.fix_active_row_path(item, self.state_saver.state.settings.blender_files_path)
    self.table.blockSignals(True)
    self.set_table_colors()
    self.table.blockSignals(False)

  def before_and_after_table_change(self, item: QTableWidgetItem | None = None) -> None:
    """Handle before and after table change."""
    self.before_table_change()
    self.after_table_change(item)

  ########### MAIN WINDOW OPS #############
  def open_settings_window(self) -> None:
    """Open the settings window."""
    self.is_saved = False
    self.window.parent().setWindowTitle("* Render Rob" + self.cache.current_file)
    settings_window.SettingsWindow(self.state_saver.state)

  def start_render(self) -> None:
    """Render operator called by the Render button."""
    self.green_jobs = []
    self.yellow_jobs = []
    self.red_jobs = []
    self.active_render_job = None
    self.window.progressBar.setValue(0)
    self.window.render_button.setEnabled(False)
    self.window.stop_button.setEnabled(True)
    self.state_saver.table_to_state(self.table)
    self._continue_render(0)
    self.table.blockSignals(False)

  def stop_render(self) -> None:
    """Interrupt the render operator."""
    if self.process:
      self.process.kill()
    self.window.progressBar.setValue(0)
    print_utils.print_info("Render stopped.")
    self.active_render_job = None
    self.window.stop_button.setEnabled(False)
    self.window.render_button.setEnabled(True)
    self.window.textBrowser.moveCursor(QTextCursor.End)

    self.set_table_colors()
    self.table.blockSignals(False)

  def play_job(self) -> int:
    """Open a job in image viewer or Blender Player."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
      self.state_saver.state.render_jobs[current_row],
      self.state_saver.state.settings.output_path,
      is_replay_mode=True,
    )
    if self.state_saver.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
        "####",
        self.state_saver.state.render_jobs[current_row].start.zfill(4),
      )
    if (
      shot_name_builder.still_or_animation(
        self.state_saver.state.render_jobs[current_row].start,
        self.state_saver.state.render_jobs[current_row].end,
      )
      == "STILL"
    ):
      if not Path(filepath).exists():
        QMessageBox.warning(self, "Warning", "The output does not yet exist.", QMessageBox.Ok)
        return
      if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", filepath))
      elif platform.system() == "Windows":  # Windows
        os.startfile(filepath)  # noqa: S606
      else:  # Linux variants
        subprocess.call(("xdg-open", filepath))
    else:
      if not Path(filepath).exists():
        QMessageBox.warning(self, "Warning", "The output does not yet exist.", QMessageBox.Ok)
      if self.state_saver.state.settings.preview.frame_step_use:
        frame_step = self.state_saver.state.settings.preview.frame_step
      else:
        frame_step = 1

      search_pattern = Path(snb.frame_path).name.replace(
        "####",
        "*",
      )
      all_frames = [str(p) for p in Path(filepath).parent.glob(search_pattern)]
      all_frames.sort()

      # The call does not take frame step and fps into account.
      # Investigated and turns out problem on Blender's side.
      subprocess.Popen(
        [
          self.state_saver.state.settings.blender_path,
          "-a",
          *all_frames,
          "-f",
          str(self.state_saver.state.settings.fps),
          "-j",
          str(frame_step),
          # Start and end frame are deliberately not passed: they are not required (at least
          # on Mac), and Blender ignores frame step and fps on this call anyway.
        ],
      )

  def open_output_folder(self) -> None:
    """Open the output folder of the currently selected job."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    if current_row == -1:
      return
    snb = shot_name_builder.ShotNameBuilder(
      self.state_saver.state.render_jobs[current_row],
      self.state_saver.state.settings.output_path,
      is_replay_mode=True,
    )
    if self.state_saver.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
        "####",
        self.state_saver.state.render_jobs[current_row].start.zfill(4),
      )
    folder_path = Path(filepath).parent
    if not folder_path.exists():
      QMessageBox.warning(self, "Warning", "The output folder does not yet exist.", QMessageBox.Ok)
      return
    if platform.system() == "Darwin":  # macOS
      subprocess.call(("open", folder_path))
    elif platform.system() == "Windows":  # Windows
      os.startfile(folder_path)  # noqa: S606
    else:  # Linux variants
      subprocess.call(("xdg-open", folder_path))

  def open_blender_file(self) -> None:
    """Open the currently selected Blender file."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    if not self.state_saver.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      QMessageBox.warning(self, "Warning", error_message, QMessageBox.Ok)
      return
    filepath = path_utils.get_abs_blend_path(
      self.state_saver.state.render_jobs[current_row].file,
      self.state_saver.state.settings.blender_files_path,
    )
    if not Path(filepath).exists():
      QMessageBox.warning(self, "Warning", "The .blend file does not exist.", QMessageBox.Ok)
      return
    # Launch Blender with the file.
    subprocess.Popen([self.state_saver.state.settings.blender_path, filepath])

  def load_settings_from_blender(self) -> None:
    """Opens Blender and syncs the settings."""
    self.table.blockSignals(True)
    self.before_table_change()

    job_index = self.table.currentRow()
    job = self.state_saver.state.render_jobs.pop(job_index)

    if not self.state_saver.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      QMessageBox.warning(self, "Warning", error_message, QMessageBox.Ok)
    filepath = path_utils.get_abs_blend_path(
      job.file,
      self.state_saver.state.settings.blender_files_path,
    )
    if filepath == "" or not Path(filepath).exists():
      QMessageBox.warning(self, "Warning", "The .blend file does not exist.", QMessageBox.Ok)
      return

    if Path("../Resources").exists():
      cwd = Path("../Resources").resolve()
    if Path("src").exists():
      cwd = Path("src").resolve()
    if platform.system() == "Windows":
      cwd = path_utils.normalize_drive_letter(str(Path.cwd()))

    python_command = [
      "import sys",
      f"sys.path.append('{cwd}')",
      "from utils_bpy import settings_loader",
    ]
    python_command = " ; ".join(python_command)
    blender_args = ["-b", filepath, "-y", "--factory-startup", "--python-expr", python_command]
    QApplication.setOverrideCursor(Qt.WaitCursor)
    subprocess.run([self.state_saver.state.settings.blender_path, *blender_args], check=True)
    QApplication.restoreOverrideCursor()
    loaded_job = self.state_saver.load_job_from_json(".sync.json")
    print_utils.print_info("Settings loaded from Blender.")
    self.state_saver.state.render_jobs.insert(job_index, loaded_job)
    self.state_saver.state_to_table(self.table)

    self.after_table_change(self.table.item(job_index, 1))
    self.table.blockSignals(False)

  ######### MAIN WINDOW UTILS ###########
  def _record_finished_job(self, exit_code: int) -> None:
    """File the job that just finished under the outcome its exit code reports."""
    if not self.active_render_job:
      return
    if exit_code in SUCCESS_EXIT_CODES:
      self.green_jobs.append(self.active_render_job)
    elif exit_code == WARNING_EXIT_CODE:
      self.yellow_jobs.append(self.active_render_job)
    elif exit_code in FAILURE_EXIT_CODES:
      self.red_jobs.append(self.active_render_job)
    else:
      msg = f"Exit code {exit_code} not recognized."
      raise ValueError(msg)

  def _continue_render(self, exit_code: int) -> None:
    """Move on to the next active render job, or finish the run."""
    self.table.blockSignals(True)
    print_utils.print_info("Continuing render.")
    # Stop the process if the stop button was pressed.
    if not self.window.stop_button.isEnabled():
      return

    self._record_finished_job(exit_code)
    self.active_render_job = None

    self.state_saver.table_to_state(self.table)

    # Get the next render job.
    for job in self.state_saver.state.render_jobs:
      if job in self.green_jobs or job in self.yellow_jobs or job in self.red_jobs:
        continue
      if not job.active:
        continue
      self.active_render_job = job
      break
    self.set_table_colors()

    if not self.active_render_job:
      print_utils.print_info("No more render jobs left.")
      self.window.progressBar.setValue(100)
      self.window.render_button.setEnabled(True)
      self.window.stop_button.setEnabled(False)
    else:
      all_jobs_count = len([x for x in self.state_saver.state.render_jobs if x.active])
      done_jobs_count = len(self.green_jobs) + len(self.yellow_jobs) + len(self.red_jobs)
      self.window.progressBar.setValue(100 * done_jobs_count / all_jobs_count)
      if self.active_render_job.active:
        self.render_job(self.active_render_job)
    self.window.textBrowser.moveCursor(QTextCursor.End)
    self.blockSignals(False)

  def _row_color_name(
    self,
    row_index: int,
    job: state_pb2.render_job,  # pylint: disable=no-member
    active_job_index: int,
  ) -> str:
    """Return the palette entry a job's row should be painted with."""
    if job in self.green_jobs:
      return "green"
    if job in self.yellow_jobs:
      return "yellow"
    if job in self.red_jobs:
      return "red"
    if not job.active:
      return "grey_inactive"
    # Highlight the active job while a render process is running.
    if row_index == active_job_index and self.window.stop_button.isEnabled():
      return "blue_grey_lighter"
    return "grey_light"

  def set_table_colors(self) -> None:
    """Set the colors of the table."""
    self.table.blockSignals(True)
    active_job_index = state_saver.find_job(
      self.state_saver.state.render_jobs,
      self.active_render_job,
    )
    for i, job in enumerate(self.state_saver.state.render_jobs):
      if i >= self.table.rowCount():
        break
      color_name = self._row_color_name(i, job, active_job_index)
      table_utils.color_row_background(self.table, i, QColor(table_utils.COLORS[color_name]))

    # Check for duplicates. The table can hold more rows than the state holds jobs while a row is
    # still being built up, so only walk the rows that have a job behind them.
    render_jobs = list(self.state_saver.state.render_jobs)
    for row_index in range(min(self.table.rowCount(), len(render_jobs))):
      if render_jobs.count(render_jobs[row_index]) > 1:
        table_utils.color_row_background(
          self.table,
          row_index,
          QColor(table_utils.COLORS["yellow"]),
        )

      # Set the background color of the blend path.
      blend_path_item = self.table.item(row_index, 1)
      if not blend_path_item:
        continue
      blend_path = Path(blend_path_item.text())
      blender_files_path = Path(self.state_saver.state.settings.blender_files_path)
      if not blend_path.exists() and not (blender_files_path / blend_path).exists():
        blend_path_item.setBackground(QColor(table_utils.COLORS["red"]))

  ########## TABLE OPS ############
  def copy_from_cell(self) -> None:
    """Copies the content of the active cell into the clipboard."""
    current_row = self.table.currentRow()
    current_column = self.table.currentColumn()
    clipboard = QApplication.clipboard()
    clipboard.setText(self.table.item(current_row, current_column).text())

  def paste_into_cell(self) -> None:
    """Pastes the content of clipboard into the active cell."""
    self.table.blockSignals(True)
    self.before_table_change()

    current_row = self.table.currentRow()
    current_column = self.table.currentColumn()
    clipboard = QApplication.clipboard()
    self.table.item(current_row, current_column).setText(clipboard.text())

    self.after_table_change()
    self.table.blockSignals(False)

  def render_job(self, job: state_pb2.render_job) -> None:  # pylint: disable=no-member
    """Render a job."""
    snb = shot_name_builder.ShotNameBuilder(job, self.state_saver.state.settings.output_path)
    inline_python = render_job_to_render_settings_setter(job, self.state_saver.state.settings)

    if shot_name_builder.still_or_animation(job.start, job.end) == "STILL":
      render_frame_command = f"-f {job.start!s}" if job.start else "-f 1"
    elif job.start:
      render_frame_command = f"-s {job.start!s} -e {job.end!s} -a"
    else:
      render_frame_command = "-a"

    self.process = QProcess()
    self.process.setProcessChannelMode(QProcess.MergedChannels)
    # Because buffering added some issues with printing, not using it for now.
    env = QProcess.systemEnvironment()
    env += "PYTHONUNBUFFERED=1"
    self.process.setEnvironment(env)

    if not self.state_saver.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      QMessageBox.warning(self, "Warning", error_message, QMessageBox.Ok)

    self.process.setProgram(self.state_saver.state.settings.blender_path)
    self.process.finished.connect(self._continue_render)

    # Check if the file was converted to a relative path.
    file_path = path_utils.get_abs_blend_path(
      job.file,
      self.state_saver.state.settings.blender_files_path,
    )
    scene_command = ["-S", job.scene] if job.scene else ""
    args = [
      "-b",
      file_path,
      "-o",
      snb.frame_path,
      "-y",
      *scene_command,
      "-F",
      ui_utils.FILE_FORMATS_COMMAND[job.file_format],
      "--python-expr",
      inline_python,
      *render_frame_command.split(" "),
    ]
    args = [i for i in args if i]
    self.process.setArguments(args)
    self.process.readyRead.connect(self._handle_output)
    self.process.start()


if __name__ == "__main__":
  main_window = MainWindow()
  sys.exit(main_window.execute())
