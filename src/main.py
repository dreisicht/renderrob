"""Main file to open RenderRob."""

import os
import platform
import subprocess
import sys
from typing import Optional

from PySide6.QtCore import QCoreApplication, QProcess, Qt
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QIcon,
    QTextCharFormat,
    QTextCursor,
)
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

        # NOTE: Avoid global state with theme colors.
        if self.app.styleHints().colorScheme().value == 1:
            table_utils.COLORS = table_utils.COLORS_LIGHT
        elif self.app.styleHints().colorScheme().value == 2:
            table_utils.COLORS = table_utils.COLORS_DARK

    def setup(self) -> None:
        """Provide main function."""
        self.app.setStyle("Breeze")
        if os.path.exists(".rr_cache"):
            self.load_cache()
        self.resize(1800, self.app.primaryScreen().size().height())
        self.window = ui_utils.load_ui_from_file(
            "ui/window.ui", custom_widgets=[DropWidget]
        )
        self.window.splitter.setSizes((200, 500))

        self.window.setWindowIcon(QIcon("icons/icon.ico"))
        self.app.setWindowIcon(QIcon("icons/icon.ico"))
        self.table = self.window.tableWidget
        self.table.setStyleSheet(
            "QTableWidget {background-color: "
            + str(table_utils.COLORS["grey_light"])
            + "}"
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
    def closeEvent(self, event: QCloseEvent):  # pylint: disable=invalid-name
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
                self.table, self.before_table_change, self.after_table_change
            )
        )
        self.window.delete_button.clicked.connect(
            lambda: table_utils.remove_active_row(
                self.table, self.before_table_change, self.after_table_change
            )
        )
        self.window.play_button.clicked.connect(self.play_job)
        self.window.open_button.clicked.connect(self.open_output_folder)
        self.window.up_button.clicked.connect(
            lambda: table_utils.move_row_up(
                self.table, self.before_table_change, self.after_table_change
            )
        )
        self.window.down_button.clicked.connect(
            lambda: table_utils.move_row_down(
                self.table, self.before_table_change, self.after_table_change
            )
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
            )
        )
        self.window.actionUndo.triggered.connect(self.undo)
        self.window.sync_button.clicked.connect(self.load_settings_from_blender)
        ui_utils.TABLE_CHANGED_FUNCTION = self.before_and_after_table_change

    ######## CACHE UTILS ##########
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
            self.window, "Save File", "", "Render Rob Files (*.rrp)"
        )
        with open(file_name, "wb") as protobuf:
            protobuf.write(self.state_saver.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
        self.cache.current_file = file_name
        self.add_filepath_to_cache(file_name)
        self.refresh_recent_files_menu()
        self.is_saved = True
        self.window.parent().setWindowTitle("Render Rob " + self.cache.current_file)

    def save_file(self) -> None:
        """Save the state to a serialized proto file without a dialog."""
        self.state_saver.table_to_state(self.table)
        with open(self.cache.current_file, "wb") as protobuf:
            protobuf.write(self.state_saver.state.SerializeToString(protobuf))  # pylint:disable=too-many-function-args
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
            action_recent = QAction(
                os.path.basename(file_path), self.window.menuOpen_Recent
            )
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
            self.window, "Open File", "", "RenderRob Files (*.rrp)"
        )
        self.open_file(file_name, ask_for_save=False)

    def open_file(self, file_name: str, ask_for_save: bool = True) -> None:
        """Open a RenderRob file."""
        self.green_jobs = []
        self.yellow_jobs = []
        self.red_jobs = []
        if ask_for_save and not self.ask_for_save():
            return
        if file_name == "":
            return
        self.table.blockSignals(True)
        with open(file_name, "rb") as pb_file:
            self.state_saver.state.ParseFromString(pb_file.read())
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

    ######### CONSOLE WINDOW ###########
    def _handle_output(self):
        """Output the subprocess output to the textbrowser widget."""
        self.table.blockSignals(True)
        data = self.process.readAll()
        output = data.data().decode()
        color_format = QTextCharFormat()
        if "\u001b" in output:
            for line in output.splitlines():
                back_color = print_utils.BASH_COLORS
                info = back_color["BACK_CYAN"] + " " + back_color["FORE_BLACK"]
                warning = back_color["BACK_YELLOW"] + " " + back_color["FORE_BLACK"]
                error = back_color["BACK_RED"] + " " + back_color["FORE_WHITE"]
                reset = back_color["RESET_ALL"]
                if line.startswith(reset):
                    line = line.replace(reset, "")
                    color_format.setBackground(QColor(table_utils.COLORS["grey_light"]))
                    color_format.setForeground(QColor(table_utils.COLORS["grey_light"]))
                if line.startswith(info):
                    line = line.replace(info, "")
                    color_format.setBackground(
                        QColor(table_utils.COLORS["blue_grey_lighter"])
                    )
                    color_format.setForeground(QColor(Qt.black))
                if line.startswith(warning):
                    line = line.replace(warning, "")
                    color_format.setBackground(QColor(table_utils.COLORS["yellow"]))
                    color_format.setForeground(QColor(Qt.black))

                    self.state_saver.table_to_state(self.table)
                    row_number = state_saver.find_job(
                        self.state_saver.state.render_jobs, self.active_render_job
                    )

                    table_utils.color_row_background(
                        self.table, row_number, QColor(table_utils.COLORS["yellow"])
                    )
                if line.startswith(error) or "blender.crash.txt" in line:
                    line = line.replace(error, "")
                    color_format.setBackground(QColor(table_utils.COLORS["red"]))
                    color_format.setForeground(QColor(table_utils.COLORS["grey_light"]))

                    self.state_saver.table_to_state(self.table)
                    row_number = state_saver.find_job(
                        self.state_saver.state.render_jobs, self.active_render_job
                    )

                    table_utils.color_row_background(
                        self.table, row_number, QColor(table_utils.COLORS["red"])
                    )

                    # Only scroll down if user is at bottom.
                if (
                    self.window.textBrowser.verticalScrollBar().value()
                    > (self.window.textBrowser.verticalScrollBar().maximum()) - 1500
                ):
                    self.window.textBrowser.moveCursor(QTextCursor.End + 1)
                self.window.textBrowser.setCurrentCharFormat(color_format)
                self.window.textBrowser.insertPlainText(line.replace(reset, "") + "\n")

                if line.endswith(reset):
                    line = line.replace(reset, "")
                    color_format.setBackground(QColor(52, 80, 100))
                    color_format.setForeground(QColor(table_utils.COLORS["grey_light"]))
        else:
            # Only scroll down if user is at bottom.
            if (
                self.window.textBrowser.verticalScrollBar().value()
                > (self.window.textBrowser.verticalScrollBar().maximum()) - 1500
            ):
                self.window.textBrowser.moveCursor(QTextCursor.End)
            self.window.textBrowser.setCurrentCharFormat(color_format)
            self.window.textBrowser.insertPlainText(output)

        # Find a more elegant way to do this.
        if "Blender quit" in output:
            self.window.textBrowser.moveCursor(QTextCursor.End)

        if "blender.crash.txt" in output:
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
        # print_utils.print_info("Before table changed.")
        self.is_saved = False
        self.window.parent().setWindowTitle("* Render Rob" + self.cache.current_file)

        self.state_saver.table_to_state(self.table)
        state_string = self.state_saver.state.SerializeToString()
        if not self.recent_states or self.recent_states[-1] != state_string:
            self.recent_states.append(state_string)

    def after_table_change(self, item: Optional[QTableWidgetItem] = None) -> None:
        """Handle after table change."""
        # print_utils.print_info("After table changed.")
        self.state_saver.table_to_state(self.table)
        if item and isinstance(item, QTableWidgetItem):
            if item.column() == 1:
                table_utils.fix_active_row_path(
                    item, self.state_saver.state.settings.blender_files_path
                )
        self.table.blockSignals(True)
        self.set_table_colors()
        self.table.blockSignals(False)

    def before_and_after_table_change(
        self, item: Optional[QTableWidgetItem] = None
    ) -> None:
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
                "####", self.state_saver.state.render_jobs[current_row].start.zfill(4)
            )
        if "STILL" == shot_name_builder.still_or_animation(
            self.state_saver.state.render_jobs[current_row].start,
            self.state_saver.state.render_jobs[current_row].end,
        ):
            if not os.path.exists(filepath):
                QMessageBox.warning(
                    self, "Warning", "The output does not yet exist.", QMessageBox.Ok
                )
                return
            if platform.system() == "Darwin":  # macOS
                subprocess.call(("open", filepath))
            elif platform.system() == "Windows":  # Windows
                os.startfile(filepath)
            else:  # Linux variants
                subprocess.call(("xdg-open", filepath))
        else:
            if not os.path.exists(filepath):
                QMessageBox.warning(
                    self, "Warning", "The output does not yet exist.", QMessageBox.Ok
                )
            if self.state_saver.state.settings.preview.frame_step_use:
                frame_step = self.state_saver.state.settings.preview.frame_step
            else:
                frame_step = 1

            # The call does not take frame step and fps into account.
            # Investigated and turns out problem on Blender's side.
            subprocess.Popen(
                [
                    self.state_saver.state.settings.blender_path,
                    "-a",
                    filepath,
                    "-f",
                    str(self.state_saver.state.settings.fps),
                    "-j",
                    str(frame_step),
                ]
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
                "####", self.state_saver.state.render_jobs[current_row].start.zfill(4)
            )
        folder_path = os.path.dirname(filepath)
        if not os.path.exists(folder_path):
            QMessageBox.warning(
                self, "Warning", "The output folder does not yet exist.", QMessageBox.Ok
            )
            return
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", folder_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(folder_path)
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
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self, "Warning", "The .blend file does not exist.", QMessageBox.Ok
            )
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
            job.file, self.state_saver.state.settings.blender_files_path
        )
        if filepath == "" or not os.path.exists(filepath):
            QMessageBox.warning(
                self, "Warning", "The .blend file does not exist.", QMessageBox.Ok
            )
            return

        cwd = path_utils.normalize_drive_letter(os.getcwd())
        python_command = [
            "import sys",
            f"sys.path.append('{cwd}')",
            "from utils_bpy import settings_loader",
        ]
        python_command = " ; ".join(python_command)
        blender_args = [
            "-b",
            filepath,
            "-y",
            "--factory-startup",
            "--python-expr",
            python_command,
        ]
        QApplication.setOverrideCursor(Qt.WaitCursor)
        subprocess.run(
            [self.state_saver.state.settings.blender_path] + blender_args, check=True
        )
        QApplication.restoreOverrideCursor()
        loaded_job = self.state_saver.load_job_from_json(".sync.json")
        print_utils.print_info("Settings loaded from Blender.")
        self.state_saver.state.render_jobs.insert(job_index, loaded_job)
        self.state_saver.state_to_table(self.table)

        self.after_table_change(self.table.item(job_index, 1))
        self.table.blockSignals(False)

    ######### MAIN WINDOW UTILS ###########
    def _continue_render(self, exit_code: int) -> None:
        self.table.blockSignals(True)
        print_utils.print_info("Continuing render.")
        # Stop the process if the stop button was pressed.
        if not self.window.stop_button.isEnabled():
            return

        # Handle the previous render job and store it in the correct list.
        if self.active_render_job:
            if exit_code in (0, 1):
                self.green_jobs.append(self.active_render_job)
            elif exit_code == 987:
                self.yellow_jobs.append(self.active_render_job)
            elif exit_code in (62097, 11):
                self.red_jobs.append(self.active_render_job)
            else:
                raise ValueError(f"Exit code {exit_code} not recognized.")

        self.active_render_job = None

        self.state_saver.table_to_state(self.table)

        # Get the next render job.
        for job in self.state_saver.state.render_jobs:
            if (
                job in self.green_jobs
                or job in self.yellow_jobs
                or job in self.red_jobs
            ):
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
            all_jobs_count = len(
                [x for x in self.state_saver.state.render_jobs if x.active]
            )
            done_jobs_count = (
                len(self.green_jobs) + len(self.yellow_jobs) + len(self.red_jobs)
            )
            self.window.progressBar.setValue(100 * done_jobs_count / all_jobs_count)
            if self.active_render_job.active:
                self.render_job(self.active_render_job)
        self.window.textBrowser.moveCursor(QTextCursor.End)
        self.blockSignals(False)

    def set_table_colors(self):
        """Set the colors of the table."""
        self.table.blockSignals(True)
        active_job_index = state_saver.find_job(
            self.state_saver.state.render_jobs, self.active_render_job
        )
        for i, job in enumerate(self.state_saver.state.render_jobs):
            if job in self.green_jobs:
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["green"])
                )
            elif job in self.yellow_jobs:
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["yellow"])
                )
            elif job in self.red_jobs:
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["red"])
                )
            elif not job.active:
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["grey_inactive"])
                )
            # Color the active job if a render process is active.
            elif i == active_job_index and self.window.stop_button.isEnabled():
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["blue_grey_lighter"])
                )
            else:
                table_utils.color_row_background(
                    self.table, i, QColor(table_utils.COLORS["grey_light"])
                )

        # Check for duplicates.
        for row_index in range(self.table.rowCount()):
            if (
                list(self.state_saver.state.render_jobs).count(
                    self.state_saver.state.render_jobs[row_index]
                )
                > 1
            ):
                table_utils.color_row_background(
                    self.table, row_index, QColor(table_utils.COLORS["yellow"])
                )

            # Set the background color of the blend path.
            blend_path_item = self.table.item(row_index, 1)
            blend_path = blend_path_item.text()
            if not os.path.exists(blend_path) and not os.path.exists(
                os.path.join(
                    self.state_saver.state.settings.blender_files_path, blend_path
                )
            ):
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
        snb = shot_name_builder.ShotNameBuilder(
            job, self.state_saver.state.settings.output_path
        )
        inline_python = render_job_to_render_settings_setter(
            job, self.state_saver.state.settings
        )

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
            job.file, self.state_saver.state.settings.blender_files_path
        )
        scene_command = f"-S {job.scene}" if job.scene else ""
        args = [
            "-b",
            file_path,
            scene_command,
            "-o",
            snb.frame_path,
            "-y",
            "-F",
            ui_utils.FILE_FORMATS_COMMAND[job.file_format],
            "--python-expr",
            inline_python,
        ]
        args = [i for i in args if i]
        args.extend(render_frame_command.split(" "))
        self.process.setArguments(args)
        # self.process.readyReadStandardOutput.connect(self._handle_output)
        self.process.readyRead.connect(self._handle_output)
        self.process.start()


if __name__ == "__main__":
    executable_dir = os.path.dirname(sys.executable)
    os.chdir(executable_dir)
    print("DEBUG: Current Working Directory:", os.getcwd())
    main_window = MainWindow()
    sys.exit(main_window.execute())
