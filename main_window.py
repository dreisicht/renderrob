"""Main file to open RenderRob."""
import os
import platform
import subprocess
import sys

from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import QAction, QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication, QFileDialog, QStyledItemDelegate

import dialogs
import settings_window
import shot_name_builder
import utils.table_utils as table_utils
import utils.ui_utils as ui_utils
from proto import cache_pb2, state_pb2
from render_job_to_rss import render_job_to_render_settings_setter
from state_saver import STATESAVER
from utils import print_utils

MAX_NUMBER_OF_RECENT_FILES = 5

COLORS = {
    "red": 0x980030,
    "yellow": 0xffd966,
    "green": 0x9fd3b6,
    "blue": 0x57a3b4,
    "blue_grey": 0x4f7997,
    "blue_grey_lighter": 0x6397bd,
    "blue_grey_darker": 0x345064,
    "neutral_grey": 0x999999,
    "black_light": 0x22282b,
    "black_dark": 0x242a2d
}


class MainWindow():
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.window = None
    self.table = None
    self.number_active_jobs = 0
    self.job_row_index = 0
    self.current_job = 0
    self.cache = cache_pb2.RenderRobCache()
    self.main()

  def main(self) -> None:
    """Provide main function."""
    app = QApplication(sys.argv)
    if os.path.exists(".rr_cache"):
      self.load_cache()

    main_window = ui_utils.load_ui_from_file("ui/window.ui")
    self.window = main_window
    self.table = main_window.tableWidget
    self.refresh_recent_files_menu()
    self.window.progressBar.setValue(0)
    self.window.progressBar.setMinimum(0)
    self.window.progressBar.setMaximum(100)
    self.make_main_window_connections()
    self.new_file()
    self.window.show()

    self.save_cache()
    sys.exit(app.exec())

  def save_cache(self) -> None:
    """Store the cache to a file."""
    cache_str = self.cache.SerializeToString()
    with open(".rr_cache", "wb") as cache_file:
      cache_file.write(cache_str)

  def load_cache(self) -> None:
    """Load the cache from a file."""
    with open(".rr_cache", "rb") as cache_file:
      cache_str = cache_file.read()
    self.cache.current_file = ""
    self.cache.ParseFromString(cache_str)

  def add_filepath_to_cache(self, file_name):
    """Add a filepath to the cache."""
    if file_name not in self.cache.recent_files:
      self.cache.recent_files.insert(0, file_name)
      if len(self.cache.recent_files) > MAX_NUMBER_OF_RECENT_FILES:
        self.cache.recent_files.pop()

  def save_as_file(self) -> None:
    """Save the state to a serialized proto file with a dialog."""
    STATESAVER.table_to_state(self.table)
    file_name, _ = QFileDialog.getSaveFileName(
        self.window, "Save File", "", "RenderRob Files (*.rrp)")
    with open(file_name, "wb") as protobuf:
      protobuf.write(STATESAVER.state.SerializeToString(protobuf))
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.refresh_recent_files_menu()

  def save_file(self) -> None:
    """Save the state to a serialized proto file without a dialog."""
    STATESAVER.table_to_state(self.table)
    with open(self.cache.current_file, "wb") as protobuf:
      protobuf.write(STATESAVER.state.SerializeToString(protobuf))

  def new_file(self) -> None:
    """Create a new file."""
    for _ in range(self.table.rowCount()):
      self.table.removeRow(0)
    self.cache.current_file = ""
    STATESAVER.state.FromString(b"")
    table_utils.post_process_row(self.table, 0)
    table_utils.add_row_below()

  def quit(self) -> None:
    """Quit the application."""
    self.save_cache()
    QCoreApplication.quit()

  def open_recent_file0(self) -> None:
    """Open the 0st recent file."""
    self.open_file(self.cache.recent_files[0])

  def open_recent_file1(self) -> None:
    """Open the 1st recent file."""
    self.open_file(self.cache.recent_files[1])

  def open_recent_file2(self) -> None:
    """Open the 2st recent file."""
    self.open_file(self.cache.recent_files[2])

  def open_recent_file3(self) -> None:
    """Open the 3st recent file."""
    self.open_file(self.cache.recent_files[3])

  def open_recent_file4(self) -> None:
    """Open the 4st recent file."""
    self.open_file(self.cache.recent_files[4])

  def clear_recent_files(self) -> None:
    """Clear the recent files."""
    del self.cache.recent_files[:]
    self.window.menuOpen_Recent.clear()
    self.recent_file_actions = []

  def refresh_recent_files_menu(self) -> None:
    """Add the recent files to the file menu."""
    self.window.menuOpen_Recent.clear()
    open_recent_functions = [
        self.open_recent_file0,
        self.open_recent_file1,
        self.open_recent_file2,
        self.open_recent_file3,
        self.open_recent_file4,
    ]
    for i, file_path in enumerate(self.cache.recent_files):
      action_recent = QAction(os.path.basename(
          file_path), self.window.menuOpen_Recent)
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
    file_name, _ = QFileDialog.getOpenFileName(
        self.window, "Open File", "", "RenderRob Files (*.rrp)")
    self.open_file(file_name)

  def open_file(self, file_name: str) -> None:
    """Open a RenderRob file."""
    with open(file_name, "rb") as pb_file:
      pb_str = pb_file.read()
    STATESAVER.state.ParseFromString(pb_str)
    STATESAVER.state_to_table(self.table)
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.cache.recent_files.remove(file_name)
    self.cache.recent_files.insert(0, file_name)
    self.refresh_recent_files_menu()

  def make_main_window_connections(self) -> None:
    """Make connections for buttons."""
    table_utils.TABLE = self.table
    self.window.add_button.clicked.connect(table_utils.add_row_below)
    self.window.delete_button.clicked.connect(table_utils.remove_active_row)
    self.window.play_button.clicked.connect(self.play_job)
    self.window.open_button.clicked.connect(self.open_output_folder)
    self.window.up_button.clicked.connect(table_utils.move_row_up)
    self.window.down_button.clicked.connect(table_utils.move_row_down)

    self.window.render_button.clicked.connect(self.start_render)
    self.window.stop_button.clicked.connect(self.stop_render)
    self.window.actionOpen.triggered.connect(self.open_file_dialog)
    self.window.actionSave.triggered.connect(self.save_file)
    self.window.actionSave_As.triggered.connect(self.save_as_file)
    self.window.actionSettings.triggered.connect(settings_window.SettingsWindow)
    self.window.actionNew.triggered.connect(self.new_file)
    self.window.actionQuit.triggered.connect(self.quit)

  def _handle_output(self):
    """Output the subprocess output to the textbrowser widget."""
    data = self.process.readAllStandardOutput()
    output = data.data().decode()
    color_format = QTextCharFormat()
    if '\u001b' in output:
      for line in output.splitlines():
        bc = print_utils.BASH_COLORS
        info = bc["BACK_CYAN"] + " " + bc["FORE_BLACK"]
        warning = bc["BACK_YELLOW"] + " " + bc["FORE_BLACK"]
        error = bc["BACK_RED"] + " " + bc["FORE_WHITE"]
        reset = bc["RESET_ALL"]
        if line.startswith(info):
          line = line.replace(info, '')
          color_format.setBackground(QColor(COLORS["blue_grey_lighter"]))
          color_format.setForeground(QColor(Qt.black))
        if line.startswith(warning):
          line = line.replace(warning, '')
          color_format.setBackground(QColor(COLORS["yellow"]))
          color_format.setForeground(QColor(Qt.black))
        if line.startswith(error):
          line = line.replace(error, '')
          color_format.setBackground(QColor(COLORS["red"]))
          color_format.setForeground(QColor(Qt.white))

        self.window.textBrowser.moveCursor(QTextCursor.End)
        self.window.textBrowser.setCurrentCharFormat(color_format)
        self.window.textBrowser.insertPlainText(line.replace(reset, "") + "\n")

        if line.endswith(reset):
          line = line.replace(reset, '')
          color_format.setBackground(QColor(52, 80, 100))
          color_format.setForeground(QColor(Qt.white))
    else:
      self.window.textBrowser.moveCursor(QTextCursor.End)
      self.window.textBrowser.setCurrentCharFormat(color_format)
      self.window.textBrowser.insertPlainText(output)

    # TODO: Find a more elegant way to do this.
    if "Blender quit" in output:
      self._refresh_progress_bar()

    # TODO #5 color a job containing a warning from the render settings setter
    # yellow and a job containing an error red.

  def _get_active_jobs_number(self) -> int:
    """Get the number of active jobs."""
    counter = 0
    for job in STATESAVER.state.render_jobs:
      if job.active:
        counter += 1
    return counter

  def play_job(self) -> int:
    """Open a job in image viewer or Blenderplayer."""
    # TODO: #6 Add support for the play of animations.
    STATESAVER.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
        STATESAVER.state.render_jobs[current_row],
        STATESAVER.state.settings.output_path,
        is_replay_mode=True)
    if STATESAVER.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
          "####",
          STATESAVER.state.render_jobs[current_row].start.zfill(4))
    if "STILL" == shot_name_builder.still_or_animation(STATESAVER.state.render_jobs[current_row].start,
                                                       STATESAVER.state.render_jobs[current_row].end):
      if not os.path.exists(filepath):
        dialogs.ErrorDialog("The output does not yet exist.")
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
      else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))
    else:
      if not os.path.exists(filepath):
        dialogs.ErrorDialog("The output does not yet exist.")
      if STATESAVER.state.settings.preview.frame_step_use:
        frame_step = STATESAVER.state.settings.preview.frame_step
      else:
        frame_step = 1
        # TODO: #7 The call might not take fps and frame step into account.
      blenderplayer_call = f"{STATESAVER.state.settings.blender_path} -a {filepath} -f {STATESAVER.state.settings.fps} -j {frame_step} -p 0 0"
      subprocess.call(blenderplayer_call)

  def open_output_folder(self) -> None:
    """Open the output folder of the currently selected job."""
    # TODO: #8 Add keyboard shortcuts.
    STATESAVER.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
        STATESAVER.state.render_jobs[current_row],
        STATESAVER.state.settings.output_path,
        is_replay_mode=True)
    if STATESAVER.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
          "####",
          STATESAVER.state.render_jobs[current_row].start.zfill(4))

    if not os.path.exists(filepath):
      dialogs.ErrorDialog("The output folder does not yet exist.")
    if platform.system() == 'Darwin':       # macOS
      folder_path = os.path.dirname(filepath)
      subprocess.call(('open', folder_path))
    elif platform.system() == 'Windows':    # Windows
      folder_path = os.path.dirname(filepath)
      os.startfile(folder_path)
    else:                                   # linux variants
      folder_path = os.path.dirname(filepath)
      subprocess.call(('xdg-open', folder_path))

  def color_row_background(self, row_index, color):
    """Color the background of a row."""
    # TODO: #3 Add coloring for upfront warnings (double jobs, animation denoising,
    # but exr selected, high quality and animation but no animation denoising,
    # single frame rendering but animation denoising,
    # single frame rendering in high quality but no denoising.)
    # FIXME: Move to separate file.
    for column_index in range(self.table.columnCount()):
      item = self.table.item(row_index, column_index)
      if item is not None:
        # FIXME: check if set style sheet is better with selections.
        item.setBackground(color)
    ui_utils.set_checkbox_background_color(
        self.table, row_index, color)
    # Note: Combobox coloring didn't work properly.
    # set_combobox_background_color is still existing though.

  def reset_all_backgruond_colors(self):
    """Reset the background colors of all rows."""
    # FIXME: Move to separate file.
    for row_index in range(self.table.rowCount()):
      self.color_row_background(row_index, QColor(Qt.white))

  def render_job(self, job: state_pb2.render_job) -> None:
    """Render a job."""
    snb = shot_name_builder.ShotNameBuilder(
        job, STATESAVER.state.settings.output_path)
    inline_python = render_job_to_render_settings_setter(
        job, STATESAVER.state.settings)

    if job.start != "" and job.end == "":
      render_frame_command = f"-f {str(job.start)}"
    elif job.start != "" and job.end != "":
      render_frame_command = f"-s {str(job.start)} -e {str(job.end)} -a"
    elif job.start == "" and job.end == "":
      render_frame_command = "-f 1"
    else:
      raise ValueError("Invalid start and end frame values.")

    self.process = QProcess()
    if not STATESAVER.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      dialogs.ErrorDialog(error_message)
    self.process.setProgram(STATESAVER.state.settings.blender_path)
    self.process.finished.connect(self._continue_render)

    args = ["-b", job.file,
            "-y",
            "-o", snb.frame_path,
            "-F", ui_utils.FILE_FORMATS[job.file_format],
            "--python-expr", inline_python,
            ]
    args.extend(render_frame_command.split(" "))
    self.process.setArguments(args)
    self.process.readyReadStandardOutput.connect(self._handle_output)
    self.process.start()

  def set_background_colors(self, exit_code: int, row_index: int) -> None:
    """Set the background colors of the rows."""
    # FIXME: Move to separate file.
    if row_index == 0:
      self.color_row_background(
          row_index, QColor(COLORS["blue_grey"]))
    else:
      if exit_code == 0:
        self.color_row_background(
            row_index - 1, QColor(COLORS["green"]))
      elif exit_code == 664:
        self.color_row_background(row_index - 1, QColor(Qt.white))
      else:
        self.color_row_background(
            row_index - 1, QColor(COLORS["red"]))
      self.color_row_background(
          row_index, QColor(COLORS["blue_grey"]))

  def _refresh_progress_bar(self):
    progress_value = int(100 / self.number_active_jobs) * self.current_job
    self.window.progressBar.setValue(progress_value)

  def _continue_render(self, exit_code: int) -> None:
    print_utils.print_info("Continuing render.")
    self.set_background_colors(exit_code, self.job_row_index)
    if STATESAVER.state.render_jobs:
      job = STATESAVER.state.render_jobs.pop(0)
      if not job.active:
        self._continue_render(664)
        self.job_row_index += 1
      else:
        print_utils.print_info(f"Starting render of {job.file}")
        self.job_row_index += 1
        self.current_job += 1
        self.render_job(job)
    else:
      print_utils.print_info("No more render jobs left.")
      self.window.progressBar.setValue(100)
      table_utils.make_editable(self.table)

  def start_render(self) -> None:
    """Render operator called by the Render button."""
    table_utils.make_read_only_selectable(self.table)
    STATESAVER.table_to_state(self.table)
    self.job_row_index = 0
    self.current_job = 0
    self.reset_all_backgruond_colors()
    self.number_active_jobs = self._get_active_jobs_number()
    self._continue_render(0)

  def stop_render(self) -> None:
    """Interrupt the render operator."""
    self.process.kill()
    del STATESAVER.state.render_jobs[:]
    self.window.progressBar.setValue(0)
    # TODO: #13 Also output the print statements to the textbrowser widget.
    self.reset_all_backgruond_colors()
    table_utils.make_editable(self.table)
    print_utils.print_info("Render stopped.")


if __name__ == "__main__":
  MainWindow()
