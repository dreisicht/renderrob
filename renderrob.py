"""Main file to open RenderRob."""
import os
import platform
import subprocess
import sys
from typing import Optional

from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor, QIcon, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (QApplication, QFileDialog, QMessageBox, QStackedLayout,
                               QTableWidgetItem, QWidget)

import settings_window
import shot_name_builder
import state_saver
from dropwidget import DropWidget
from proto import cache_pb2, state_pb2
from render_job_to_rss import render_job_to_render_settings_setter
from utils import print_utils, table_utils, ui_utils

MAX_NUMBER_OF_RECENT_FILES = 5


class MainWindow(QWidget):
  """Main window for RenderRob."""
  ########### SETUP ############

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
    self.state_saver = state_saver.StateSaver()

    self.recent_file_actions = None
    self.process = None
    self.is_saved = True
    self.recent_states = []

  def setup(self) -> None:
    """Provide main function."""
    self.app.setStyle("Breeze")
    if os.path.exists(".rr_cache"):
      self.load_cache()
    self.resize(1800, self.app.primaryScreen().size().height() - 100)
    self.window = ui_utils.load_ui_from_file("ui/window.ui", custom_widgets=[DropWidget])
    self.window.splitter.setSizes((200, 500))

    self.window.setWindowIcon(QIcon("icons/icon.ico"))
    self.app.setWindowIcon(QIcon("icons/icon.ico"))
    self.window.setWindowTitle("RenderRob")
    self.table = self.window.tableWidget  # XXX: needed?
    self.refresh_recent_files_menu()
    self.window.progressBar.setValue(0)
    self.window.progressBar.setMinimum(0)
    self.window.progressBar.setMaximum(100)
    layout = QStackedLayout()
    layout.addWidget(self.window)
    self.setLayout(layout)
    self.make_main_window_connections()

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
  def closeEvent(self, event: QCloseEvent):  # pylint: disable=invalid-name
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

  def quit(self) -> None:
    """Quit the application."""
    self.save_cache()
    QCoreApplication.quit()

  def make_main_window_connections(self) -> None:
    """Make connections for buttons."""
    self.window.add_button.clicked.connect(lambda: self.add_row_below(register_undo=True))
    self.window.delete_button.clicked.connect(self.remove_active_row)
    self.window.play_button.clicked.connect(self.play_job)
    self.window.open_button.clicked.connect(self.open_output_folder)
    self.window.up_button.clicked.connect(lambda: table_utils.move_row_up(self.table))
    self.window.down_button.clicked.connect(lambda: table_utils.move_row_down(self.table))

    self.window.render_button.clicked.connect(self.start_render)
    self.window.stop_button.clicked.connect(self.stop_render)
    self.window.actionOpen.triggered.connect(self.open_file_dialog)
    self.window.actionSave.triggered.connect(self.save_file)
    self.window.actionSave_As.triggered.connect(self.save_as_file)
    self.window.actionSettings.triggered.connect(self.open_settings_window)
    self.window.actionNew.triggered.connect(self.new_file)
    self.window.actionQuit.triggered.connect(self.quit)
    self.table.itemChanged.connect(self.table_item_changed)
    self.window.blender_button.clicked.connect(self.open_blender_file)
    self.window.duplicate_button.clicked.connect(self.duplicate_row)
    self.window.actionUndo.triggered.connect(self.undo)

  ##### FILE OPS#####

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
    self.state_saver.table_to_state(self.table)
    file_name, _ = QFileDialog.getSaveFileName(
        self.window, "Save File", "", "RenderRob Files (*.rrp)")
    with open(file_name, "wb") as protobuf:
      protobuf.write(
          self.state_saver.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.refresh_recent_files_menu()
    self.is_saved = True
    self.window.setWindowTitle("RenderRob " + self.cache.current_file)

  def save_file(self) -> None:
    """Save the state to a serialized proto file without a dialog."""
    self.state_saver.table_to_state(self.table)
    with open(self.cache.current_file, "wb") as protobuf:
      protobuf.write(
          self.state_saver.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
    self.is_saved = True
    self.window.setWindowTitle("RenderRob " + self.cache.current_file)

  def new_file(self) -> None:
    """Create a new file."""
    for _ in range(self.table.rowCount()):
      self.table.removeRow(0)
    self.cache.current_file = ""
    self.state_saver.state.FromString(b"")
    self.state_saver.parent_widget = self
    self.recent_states = [b""]
    table_utils.post_process_row(self.table, 0)
    self.add_row_below(register_undo=False)

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
    self.table.blockSignals(True)
    with open(file_name, "rb") as pb_file:
      self.state_saver.state.ParseFromString(pb_file.read())
    self.state_saver.state_to_table(self.table)
    self.cache.current_file = file_name
    self.add_filepath_to_cache(file_name)
    self.cache.recent_files.remove(file_name)
    self.cache.recent_files.insert(0, file_name)
    self.refresh_recent_files_menu()
    self.recent_states = [self.state_saver.state.SerializeToString()]
    self.table.blockSignals(False)

  ######### CONSOLE WINDOW ###########

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

  def table_item_changed(self, item: Optional[QTableWidgetItem] = None) -> None:
    """Handle table item changes."""
    print_utils.print_info("Table item changed.")
    self.is_saved = False
    self.window.setWindowTitle("RenderRob * " + self.cache.current_file)

    self.state_saver.table_to_state(self.table)
    state_string = self.state_saver.state.SerializeToString()
    if not self.recent_states or self.recent_states[-1] != state_string:
      self.recent_states.append(state_string)
    if item:
      self.table.blockSignals(True)
      if item.column() == 1:
        table_utils.fix_active_row_path(item, self.state_saver.state.settings.blender_files_path)
        if not os.path.exists(item.text()) and not os.path.exists(os.path.join(self.state_saver.state.settings.blender_files_path, item.text())):
          QMessageBox.warning(self, "Warning", "The .blend file does not exist.", QMessageBox.Ok)
      self.table.blockSignals(False)
    self.check_table_for_errors()

  ########### MAIN WINDOW OPS #############
  def open_settings_window(self) -> None:
    """Open the settings window."""
    self.is_saved = False
    self.window.setWindowTitle("RenderRob * " + self.cache.current_file)
    settings_window.SettingsWindow(self.state_saver.state)

  def start_render(self) -> None:
    """Render operator called by the Render button."""
    self.table.blockSignals(True)
    self.window.progressBar.setValue(0)
    self.window.render_button.setEnabled(False)
    table_utils.make_read_only_selectable(self.table)
    self.state_saver.table_to_state(self.table)
    self.job_row_index = 0
    self.current_job = 0
    table_utils.reset_all_backgruond_colors(self.table)
    self.number_active_jobs = self._get_active_jobs_number()
    self._continue_render(0)
    self.table.blockSignals(False)

  def stop_render(self) -> None:
    """Interrupt the render operator."""
    self.process.kill()
    del self.state_saver.state.render_jobs[:]
    self.window.progressBar.setValue(0)
    table_utils.make_editable(self.table)
    print_utils.print_info("Render stopped.")
    self.window.render_button.setEnabled(True)

  def play_job(self) -> int:
    """Open a job in image viewer or Blender Player."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
        self.state_saver.state.render_jobs[current_row],
        self.state_saver.state.settings.output_path,
        is_replay_mode=True)
    if self.state_saver.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
          "####",
          self.state_saver.state.render_jobs[current_row].start.zfill(4))
    if "STILL" == shot_name_builder.still_or_animation(
            self.state_saver.state.render_jobs[current_row].start,
            self.state_saver.state.render_jobs[current_row].end):
      if not os.path.exists(filepath):
        QMessageBox.warning(self, "Warning", "The output does not yet exist.", QMessageBox.Ok)
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
      else:                                   # Linux variants
        subprocess.call(('xdg-open', filepath))
    else:
      if not os.path.exists(filepath):
        QMessageBox.warning(self, "Warning", "The output does not yet exist.", QMessageBox.Ok)
      if self.state_saver.state.settings.preview.frame_step_use:
        frame_step = self.state_saver.state.settings.preview.frame_step
      else:
        frame_step = 1

      # The call does not take frame step and fps into account.
      # Investigated and turns out problem on Blender's side.
      subprocess.Popen([self.state_saver.state.settings.blender_path, "-a", filepath,
                       "-f", str(self.state_saver.state.settings.fps), "-j", str(frame_step)])

  def open_output_folder(self) -> None:
    """Open the output folder of the currently selected job."""
    # #8 Add keyboard shortcuts.
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    snb = shot_name_builder.ShotNameBuilder(
        self.state_saver.state.render_jobs[current_row],
        self.state_saver.state.settings.output_path,
        is_replay_mode=True)
    if self.state_saver.state.render_jobs[current_row].start == "":
      filepath = snb.frame_path.replace("####", "0001").replace("v$$", "v01")
    else:
      filepath = snb.frame_path.replace(
          "####",
          self.state_saver.state.render_jobs[current_row].start.zfill(4))
    folder_path = os.path.dirname(filepath)
    if not os.path.exists(folder_path):
      QMessageBox.warning(self, "Warning", "The output folder does not yet exist.", QMessageBox.Ok)
      return
    if platform.system() == 'Darwin':       # macOS
      subprocess.call(('open', folder_path))
    elif platform.system() == 'Windows':    # Windows
      os.startfile(folder_path)
    else:                                   # Linux variants
      subprocess.call(('xdg-open', folder_path))

  def open_blender_file(self) -> None:
    """Open the currently selected Blender file."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    if not self.state_saver.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      QMessageBox.warning(self, "Warning", error_message, QMessageBox.Ok)
      return
    filepath = ui_utils.get_blend_path(self.state_saver.state.render_jobs[current_row].file,
                                       self.state_saver.state.settings.blender_files_path)
    if not os.path.exists(filepath):
      QMessageBox.warning(self, "Warning", "The .blend file does not exist.", QMessageBox.Ok)
      return
    # Launch Blender with the file.
    subprocess.Popen([self.state_saver.state.settings.blender_path, filepath])

  ######### MAIN WINDOW UTILS ###########

  def _refresh_progress_bar(self) -> None:
    progress_value = int(100 / self.number_active_jobs) * self.current_job
    self.window.progressBar.setValue(progress_value)

  def _continue_render(self, exit_code: int) -> None:
    self.table.blockSignals(True)
    # 62097 is the exit code for an interrupted process -> cancelled render.
    table_utils.set_background_colors(self.table, exit_code, self.job_row_index)
    print_utils.print_info("Continuing render.")
    if self.state_saver.state.render_jobs:
      job = self.state_saver.state.render_jobs.pop(0)
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
    self.blockSignals(False)

  ########## TABLE OPS ############

  def render_job(self, job: state_pb2.render_job) -> None:  # pylint: disable=no-member
    """Render a job."""
    snb = shot_name_builder.ShotNameBuilder(
        job, self.state_saver.state.settings.output_path)
    inline_python = render_job_to_render_settings_setter(
        job, self.state_saver.state.settings)

    if "STILL" == shot_name_builder.still_or_animation(job.start, job.end):
      if job.start:
        render_frame_command = f"-f {str(job.start)}"
      else:
        render_frame_command = "-f 1"
    else:
      if job.start:
        render_frame_command = f"-s {str(job.start)} -e {str(job.end)} -a"
      else:
        render_frame_command = "-a"

    self.process = QProcess()
    if not self.state_saver.state.settings.blender_path:
      error_message = "The Blender path is not set."
      print_utils.print_error_no_exit(error_message)
      QMessageBox.warning(self, "Warning", error_message, QMessageBox.Ok)
    self.process.setProgram(self.state_saver.state.settings.blender_path)
    self.process.finished.connect(self._continue_render)

    # Check if the file was converted to a relative path.
    file_path = ui_utils.get_blend_path(
        job.file, self.state_saver.state.settings.blender_files_path)
    args = ["-b", file_path,
            "-y",
            "-o", snb.frame_path,
            "-F", ui_utils.FILE_FORMATS_COMMAND[job.file_format],
            "--python-expr", inline_python,
            ]
    args.extend(render_frame_command.split(" "))
    self.process.setArguments(args)
    self.process.readyReadStandardOutput.connect(self._handle_output)
    self.process.start()

  def duplicate_row(self) -> None:
    """Duplicate the currently selected row."""
    self.state_saver.table_to_state(self.table)
    current_row = self.table.currentRow()
    self.state_saver.state.render_jobs.insert(
        current_row + 1, self.state_saver.state.render_jobs[current_row])
    self.table.blockSignals(True)
    self.state_saver.state_to_table(self.table)
    self.table_item_changed()
    self.table.blockSignals(False)

  def add_row_below(self, register_undo=True) -> None:
    """Add a row below the current row."""
    self.table.blockSignals(True)
    current_row = self.table.currentRow() + 1
    self.table.insertRow(current_row)
    ui_utils.fill_row(self.table, current_row)
    table_utils.set_text_alignment(self.table, current_row)
    if register_undo:
      self.table_item_changed()
    self.table.blockSignals(False)

  def remove_active_row(self) -> None:
    """Remove the currently selected row."""
    self.table.blockSignals(True)
    current_row = self.table.currentRow()
    if current_row == -1:
      current_row = self.table.rowCount() - 1
    self.table.removeRow(current_row)
    self.table.blockSignals(False)
    self.table_item_changed()

  ########### TABLE UTILS #############

  def check_table_for_errors(self) -> bool:
    """Check the table for errors."""
    # Double occurrences of jobs
    self.table.blockSignals(True)
    for i in range(self.table.rowCount()):
      if list(self.state_saver.state.render_jobs).count(self.state_saver.state.render_jobs[i]) > 1:
        table_utils.color_row_background(self.table, i, QColor(table_utils.COLORS["yellow"]))
      else:
        table_utils.color_row_background(self.table, i, QColor(table_utils.COLORS["grey_light"]))
    self.table.blockSignals(False)
    # Ignoring animation denoising for now, since # it's deprecated in Blender.

  def _get_active_jobs_number(self) -> int:
    """Get the number of active jobs."""
    counter = 0
    for job in self.state_saver.state.render_jobs:
      if job.active:
        counter += 1
    return counter


if __name__ == "__main__":
  main_window = MainWindow()
  sys.exit(main_window.execute())
