"""Main file to open RenderRob."""
import os
import platform
import subprocess
import sys

from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import QAction, QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication, QFileDialog

import settings_window
import shot_name_builder
import utils.table_utils as table_utils
import utils.ui_utils as ui_utils
from proto import cache_pb2, state_pb2
from render_job_to_rss import render_job_to_render_settings_setter
from state_saver import STATESAVER

MAX_NUMBER_OF_RECENT_FILES = 5


class MainWindow():
  """Main window for RenderRob."""

  def __init__(self) -> None:
    """Initialize the main window."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.window = None
    self.table = None
    self.number_active_jobs = 0
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
    """Output the subprocess output to the QTextEdit widget."""
    data = self.process.readAllStandardOutput()
    output = data.data().decode()
    color_format = QTextCharFormat()
    if '\u001b[46m' in output:
      color_format.setForeground(QColor(Qt.white))
      color_format.setBackground(QColor(Qt.blue))
    elif '\u001b[30m' in output:
      color_format.setForeground(QColor(Qt.black))
      color_format.setBackground(QColor(Qt.white))

    self.window.textBrowser.moveCursor(QTextCursor.End)
    self.window.textBrowser.setCurrentCharFormat(color_format)
    self.window.textBrowser.insertPlainText(output)

    if "Blender quit" in output:
      progress_value_current = self.window.progressBar.value()
      progress_value = int(100 / self.number_active_jobs)
      self.window.progressBar.setValue(
          progress_value_current + progress_value)

  def _get_active_jobs_number(self) -> int:
    """Get the number of active jobs."""
    counter = 0
    for job in STATESAVER.state.render_jobs:
      if job.active:
        counter += 1
    return counter

  def play_job(self) -> int:
    """Open a job in image viewer or Blenderplayer."""
    STATESAVER.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
        STATESAVER.state.render_jobs[current_row],
        STATESAVER.state.settings.output_path)
    if STATESAVER.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
          "####",
          STATESAVER.state.render_jobs[current_row].start.zfill(4))
    if platform.system() == 'Darwin':       # macOS
      subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
      print(filepath)
      os.startfile(filepath)
    else:                                   # linux variants
      subprocess.call(('xdg-open', filepath))

  def open_output_folder(self) -> None:
    """Open the output folder of the currently selected job."""
    pass

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
    print("Starting Render process.")
    self.process.start()

  def _continue_render(self) -> None:
    # Ignoring exit_code and QProcess.ExitStatus for now.
    if STATESAVER.state.render_jobs:
      job = STATESAVER.state.render_jobs.pop(0)
      if not job.active:
        self._continue_render()
      else:
        self.render_job(job)

  def start_render(self) -> None:
    """Render operator called by the Render button."""
    STATESAVER.table_to_state(self.table)
    self.number_active_jobs = self._get_active_jobs_number()
    self._continue_render()

  def stop_render(self) -> None:
    """Interrupt the render operator."""
    self.process.kill()
    self.window.progressBar.setValue(0)


if __name__ == "__main__":
  MainWindow()
