"""Main file to open RenderRob."""
import os
import platform
import subprocess
import sys

from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QTextCharFormat, QTextCursor, QCloseEvent
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget, QMainWindow, QVBoxLayout, QStackedLayout, QGridLayout

import dialogs
import settings_window
import shot_name_builder
from proto import cache_pb2, state_pb2
from render_job_to_rss import render_job_to_render_settings_setter
from state_saver import STATESAVER
from utils import print_utils, table_utils, ui_utils

MAX_NUMBER_OF_RECENT_FILES = 5


class MainWindow(QWidget):
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.app = QApplication(sys.argv)
    super().__init__()
    self.window = None
    self.table = None
    self.number_active_jobs = 0
    self.job_row_index = 0
    self.current_job = 0
    self.cache = cache_pb2.RenderRobCache()  # pylint: disable=no-member
    self.recent_file_actions = None
    self.process = None
    self.is_saved = True

  def setup(self) -> None:
    """Provide main function."""
    self.app.setStyle("Breeze")
    if os.path.exists(".rr_cache"):
      self.load_cache()
    self.window = ui_utils.load_ui_from_file("ui/window.ui")

    self.resize(1400, self.app.primaryScreen().size().height() - 100)
    self.window.setWindowIcon(QIcon("icons/icon.ico"))
    self.app.setWindowIcon(QIcon("icons/icon.ico"))
    self.window.setWindowTitle("RenderRob")
    self.table = self.window.tableWidget
    self.refresh_recent_files_menu()
    self.window.progressBar.setValue(0)
    self.window.progressBar.setMinimum(0)
    self.window.progressBar.setMaximum(100)
    self.make_main_window_connections()
    layout = QStackedLayout()
    layout.addWidget(self.window)
    self.setLayout(layout)

  def closeEvent(self, event):
    """Handle the close event."""
    if self.is_saved:
      event.accept()
      return
    reply = QMessageBox.question(self, 'Message', 'Are you sure you want to quit?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()

  def execute(self) -> None:
    """Execute the main window.

    NOTE: For unit testing, this function should not be called.
    """
    self.setup()
    self.new_file()
    self.show()
    self.save_cache()
    self.app.exec()

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
      protobuf.write(
          STATESAVER.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.refresh_recent_files_menu()
    self.is_saved = True

  def save_file(self) -> None:
    """Save the state to a serialized proto file without a dialog."""
    STATESAVER.table_to_state(self.table)
    with open(self.cache.current_file, "wb") as protobuf:
      protobuf.write(
          STATESAVER.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
    self.is_saved = True

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

  def open_settings_window(self) -> None:
    """Open the settings window."""
    self.is_saved = False
    settings_window.SettingsWindow()

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
    self.window.actionSettings.triggered.connect(self.open_settings_window)
    self.window.actionNew.triggered.connect(self.new_file)
    self.window.actionQuit.triggered.connect(self.quit)
    #  #20 Add open blender button

  def _handle_output(self):
    """Output the subprocess output to the textbrowser widget."""
    data = self.process.readAllStandardOutput()
    output = data.data().decode()
    color_format = QTextCharFormat()
    if '\u001b' in output:
      for line in output.splitlines():
        back_color = print_utils.BASH_COLORS
        info = back_color["BACK_CYAN"] + " " + back_color["FORE_BLACK"]
        warning = back_color["BACK_YELLOW"] + " " + back_color["FORE_BLACK"]
        error = back_color["BACK_RED"] + " " + back_color["FORE_WHITE"]
        reset = back_color["RESET_ALL"]
        if line.startswith(info):
          line = line.replace(info, '')
          color_format.setBackground(
              QColor(table_utils.COLORS["blue_grey_lighter"]))
          color_format.setForeground(QColor(Qt.black))
        if line.startswith(warning):
          line = line.replace(warning, '')
          color_format.setBackground(QColor(table_utils.COLORS["yellow"]))
          color_format.setForeground(QColor(Qt.black))
          table_utils.color_row_background(self.table,
                                           self.job_row_index - 1,
                                           QColor(table_utils.COLORS["yellow"]))
          table_utils.set_background_colors(self.table, 987, self.job_row_index)

        if line.startswith(error):
          line = line.replace(error, '')
          color_format.setBackground(QColor(table_utils.COLORS["red"]))
          color_format.setForeground(QColor(table_utils.COLORS["grey_light"]))

        self.window.textBrowser.moveCursor(QTextCursor.End)
        self.window.textBrowser.setCurrentCharFormat(color_format)
        self.window.textBrowser.insertPlainText(line.replace(reset, "") + "\n")

        if line.endswith(reset):
          line = line.replace(reset, '')
          color_format.setBackground(QColor(52, 80, 100))
          color_format.setForeground(QColor(table_utils.COLORS["grey_light"]))
    else:
      self.window.textBrowser.moveCursor(QTextCursor.End)
      self.window.textBrowser.setCurrentCharFormat(color_format)
      self.window.textBrowser.insertPlainText(output)

    #  Find a more elegant way to do this.
    if "Blender quit" in output:
      self._refresh_progress_bar()
      self.window.textBrowser.insertPlainText("\n")
      self.window.textBrowser.moveCursor(QTextCursor.End)

  def _get_active_jobs_number(self) -> int:
    """Get the number of active jobs."""
    counter = 0
    for job in STATESAVER.state.render_jobs:
      if job.active:
        counter += 1
    return counter

  def play_job(self) -> int:
    """Open a job in image viewer or Blender Player."""
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
    if "STILL" == shot_name_builder.still_or_animation(
            STATESAVER.state.render_jobs[current_row].start,
            STATESAVER.state.render_jobs[current_row].end):
      if not os.path.exists(filepath):
        dialogs.ErrorDialog("The output does not yet exist.")
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
      else:                                   # Linux variants
        subprocess.call(('xdg-open', filepath))
    else:
      if not os.path.exists(filepath):
        dialogs.ErrorDialog("The output does not yet exist.")
      if STATESAVER.state.settings.preview.frame_step_use:
        frame_step = STATESAVER.state.settings.preview.frame_step
      else:
        frame_step = 1

      # The call does not take frame step and fps into account.
      # Investigated and turns out problem on Blender's side.
      blenderplayer_call = (f"{STATESAVER.state.settings.blender_path} -a {filepath} -f"
                            f"{STATESAVER.state.settings.fps} -j {frame_step} -p 0 0")
      subprocess.call(blenderplayer_call)

  def open_output_folder(self) -> None:
    """Open the output folder of the currently selected job."""
    # #8 Add keyboard shortcuts.
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
    else:                                   # Linux variants
      folder_path = os.path.dirname(filepath)
      subprocess.call(('xdg-open', folder_path))

  def render_job(self, job: state_pb2.render_job) -> None:  # pylint: disable=no-member
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

  def _refresh_progress_bar(self) -> None:
    progress_value = int(100 / self.number_active_jobs) * self.current_job
    self.window.progressBar.setValue(progress_value)

  def _continue_render(self, exit_code: int) -> None:
    # 62097 is the exit code for an interrupted process -> cancelled render.
    table_utils.set_background_colors(self.table, exit_code, self.job_row_index)
    print_utils.print_info("Continuing render.")
    if STATESAVER.state.render_jobs:
      job = STATESAVER.state.render_jobs.pop(0)
      if not job.active:
        self.job_row_index += 1
        self._continue_render(664)
      else:
        print_utils.print_info(f"Starting render of {job.file}")
        self.job_row_index += 1
        self.current_job += 1
        self.render_job(job)
    else:
      print_utils.print_info("No more render jobs left.")
      self.window.progressBar.setValue(100)
      table_utils.make_editable(self.table)
      self.window.render_button.setEnabled(True)

  def start_render(self) -> None:
    """Render operator called by the Render button."""
    self.window.progressBar.setValue(0)
    self.window.render_button.setEnabled(False)
    table_utils.make_read_only_selectable(self.table)
    STATESAVER.table_to_state(self.table)
    self.job_row_index = 0
    self.current_job = 0
    table_utils.reset_all_backgruond_colors(self.table)
    self.number_active_jobs = self._get_active_jobs_number()
    self._continue_render(0)

  def stop_render(self) -> None:
    """Interrupt the render operator."""
    self.process.kill()
    del STATESAVER.state.render_jobs[:]
    self.window.progressBar.setValue(0)
    table_utils.make_editable(self.table)
    print_utils.print_info("Render stopped.")
    self.window.render_button.setEnabled(True)


if __name__ == "__main__":
  main_window = MainWindow()
  sys.exit(main_window.execute())
