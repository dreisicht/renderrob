import os
import sys
import glob
import xlrd
import threading
import subprocess
import signal
from time import sleep
from datetime import datetime
from sty import fg, bg, ef, rs, Style, RgbBg
import sty
from rr_gspread import query_sheet
from subprocess import Popen
import rr_image

if "win" in sys.platform:
    from subprocess import CREATE_NEW_CONSOLE

class jobs(object):
    def __init__(self):
        self.print_info("Hello from Render Rob! I'm glad to help you!")

        self.currentpath = os.path.dirname(
            os.path.realpath(__file__)).replace("\\", "/")+"/"
        self.flush_cache_file()
        # print(glob.glob(self.currentpath + "*.xlsx"))
        excel_file = glob.glob(self.currentpath + "*.xlsx")
        if len(excel_file) > 0:
            self.jobs_table, global_set = self.rr_read_excel(
                excel_file[0].replace("\\", "/"))
            self.print_info("I found an Excel file. I'm gonna use that one!")
            # print(self.jobs_table, global_set)
        else:
            try:
                self.print_info(
                    "I'm gonna go and get the data from Google Sheets.")
                self.jobs_table, global_set = query_sheet()
                self.print_info(
                    "I successfully downloaded the data from Google Sheets.")
            except ArithmeticError:
                self.print_error(
                    "Couldn't get the data from Google Sheets. Please try installing Render Rob again!")
            # print(self.jobs_table, global_set)

        self.blenderpath = self.path_process(global_set[0][1])[:-1]
        self.renderpath = self.path_process(global_set[1][1])
        self.blendfolder = self.path_process(global_set[2][1])
        try:
            self.add_on_list = global_set[6][1].replace(", ", ",").split(",")
        except IndexError:
            self.add_on_list = ""

        # remove empty elements
        self.add_on_list = [x for x in self.add_on_list if x]

        # defining colors here
        self.red = self.hex_to_rgb("980030")
        self.green = self.hex_to_rgb("499a6c")
        self.yellow = self.hex_to_rgb("ffd966")
        self.grey = self.hex_to_rgb("999999")
        self.light_blue = self.hex_to_rgb("78909c")
        self.dark_blue = self.hex_to_rgb("45818e")
        self.lighter_stone = self.hex_to_rgb("242a2d")
        self.dark_stone = self.hex_to_rgb("22282b")

        bg.red = Style(RgbBg(self.red[0], self.red[1], self.red[2]))
        bg.green = Style(RgbBg(self.green[0], self.green[1], self.green[2]))
        bg.yellow = Style(
            RgbBg(self.yellow[0], self.yellow[1], self.yellow[2]))
        bg.grey = Style(RgbBg(self.grey[0], self.grey[1], self.grey[2]))
        bg.light_blue = Style(
            RgbBg(self.light_blue[0], self.light_blue[1], self.light_blue[2]))
        bg.dark_blue = Style(
            RgbBg(self.dark_blue[0], self.dark_blue[1], self.dark_blue[2]))
        bg.lighter_stone = Style(
            RgbBg(self.lighter_stone[0], self.lighter_stone[1], self.lighter_stone[2]))
        bg.dark_stone = Style(
            RgbBg(self.dark_stone[0], self.dark_stone[1], self.dark_stone[2]))

        self.error_cache_len = 0

        # check if blender path is filled out correctly
        if self.blenderpath == "C:/Path/To/Blender.exe":
            self.print_error("Please fill the path to blender under globals!")
            sys.exit()
        elif self.blenderpath == "blender":
            pass
        elif not os.path.isfile(self.blenderpath):
            self.print_error(
                "I couldn't find Blender under {}. Perhaps a spelling mistake?".format(self.blenderpath))
            sys.exit()

        # check if render path is filled out correctly
        if self.renderpath == "C:/Path/To/My/Renders/":
            self.print_error(
                "Please fill the path to you render folder under globals!")
            sys.exit()
        elif not os.path.exists(self.renderpath):
            self.print_error(
                "I couldn't find the render output folder. Perhaps a spelling mistake?")
            sys.exit()

        if not os.path.exists(self.blendfolder):
            self.print_warning(
                "I couldn't find the .blend file folder. Perhaps a spelling mistake?")

        self.preview_res = global_set[3][1]
        self.preview_res_active = self.tobool(global_set[3][2])

        self.preview_samples = global_set[4][1]
        self.preview_samples_active = self.tobool(global_set[4][2])

        self.preview_framestep = global_set[5][1]
        self.preview_framestep_active = self.tobool(global_set[5][2])

        self.shot_iter_num = 1

        self.thread_cpu = None
        self.thread_gpu = None
        self.thread_gpu_an_dn = None

    def flush_cache_file(self):
        f = open(self.currentpath + "cache/ERRORCACHE", "w")
        f.write("")
        f.close()

    def read_errors(self):
        # open and read the file after the appending:
        try:
            f = open(self.currentpath + "cache/ERRORCACHE", "r")
        except PermissionError:
            sleep(0.1)
            f = open(self.currentpath + "cache/ERRORCACHE", "r")
        finally:
            sleep(0.1)

        tmp_str = f.read()

        f.close()
        print_list = []

        error_list = tmp_str[self.error_cache_len:].split("\n")
        self.error_cache_len = len(tmp_str)

        for line in error_list:
            if line not in print_list:
                if "[ERROR]" in line:
                    self.print_error_noinput(line.replace("[ERROR]", ""))
                elif "[WARNING]" in line:
                    self.print_warning_noinput(line.replace("[WARNING]", ""))
            print_list.append(line)

    def rr_read_excel(self, path_sheet):
        wb = xlrd.open_workbook(path_sheet)
        jobs_sheet = wb.sheet_by_index(0)
        global_sheet = wb.sheet_by_index(1)

        return self.fill_array(jobs_sheet), self.fill_array(global_sheet)

    @staticmethod
    def hex_to_rgb(h):
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    # print methods
    @staticmethod
    def print_error(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.red + fg.white + time_current +
              " [ERROR] " + ipt_str + " Press Enter to exit." + rs.all)
        sys.exit()

    @staticmethod
    def print_error_noinput(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(bg.red + fg.white + time_current +
              " [ERROR] " + ipt_str + rs.all)

    @staticmethod
    def print_warning(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.yellow + fg.black + time_current +
              "[WARNING] " + ipt_str + " Press Enter to continue." + rs.all)

    @staticmethod
    def print_warning_noinput(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(bg.yellow + fg.black + time_current +
              " [WARNING]" + ipt_str + rs.all)

    @staticmethod
    def print_info_input(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.dark_blue + fg.white + time_current +
              "[INFO] " + ipt_str + " Press Enter to continue." + rs.all)

    @staticmethod
    def print_info(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(time_current, ipt_str)

    @staticmethod
    def fill_array(query_object):
        mydata = []
        for row in range(query_object.nrows):
            # stop if line is empty
            if query_object.cell_value(row, 1) == "":
                break

            # create sub list
            sub = []
            for column in range(query_object.ncols):
                value = query_object.cell_value(row, column)
                if type(value) is float:
                    value = int(value)
                sub.append(value)
            mydata.append(sub)
        return mydata

    @staticmethod
    def path_process(path_string):
        path_string = path_string.replace(
            "\\", "/").replace('"', '').replace("'", "")
        if len(path_string) < 1:
            return ''
        if path_string[-1] != "/":
            return path_string + "/"
        else:
            return path_string

    @staticmethod
    def tobool(bool_val):
        if type(bool_val) == str:
            if bool_val.upper() == "FALSE":
                return False
            elif bool_val.upper() == "TRUE":
                return True
            else:
                print("Bool Error")
        elif type(bool_val) == int:
            if bool_val == 0:
                return False
            elif bool_val == 1:
                return True
        else:
            print("Bool Error")

    def get_shotname(self):
        # preview or hq suffix
        if self.hq:
            self.quality_state_string = "hq"
        else:
            self.quality_state_string = "pv"

        # get blender file name without .blend

        self.view_layer_dir = ",".join(
            self.view_layer).replace("View Layer", "Vl")

        filename = self.blendpath.split("/")[-1][:-6]
        self.shotname = (filename + "-" +
                         self.active_camera.replace("Camera", "Cam") + "-" +
                         #  str(self.startframe) + "-" +
                         #  str(self.endframe) + "-" +
                         str(self.scene.replace("Scene", "Sc")) + "-" +
                         str(self.view_layer_dir) + "-" +
                         self.quality_state_string + "-v")
        self.shotname = self.shotname.replace(" ", "_")

    def assemble_frame_path(self):
        return (self.frame_render_folder + self.shotname + "$$" +
                "-" + "####." + self.file_format)

    def get_frame_path(self):
        '''inputs:
        self.renderpath
        self.shotname
        self.endframe

        output:
        *self.full_frame_path*

        full_frame_path is a string, which points either to a folder (animation rendering),
        or to a single image (still image rendering)

        '''
        self.shot_iter_num = 1

        # Different folder for still images and animations
        # If still image rendering
        if self.endframe == "" and self.startframe != "":
            self.frame_render_folder = self.renderpath + "stills/"
        # if animation rendering
        else:
            self.frame_render_folder = self.renderpath + self.shotname + "$$/"

        self.full_frame_path_no_ver = self.assemble_frame_path()

        # while image with given iteration number ist existing, raise iteration number
        while os.path.exists(self.full_frame_path_no_ver.replace("$$", str(self.shot_iter_num).zfill(2)).replace("####", str(self.startframe).zfill(4))):
            self.shot_iter_num = self.shot_iter_num + 1

        if not self.new_version and self.shot_iter_num > 1:
            self.shot_iter_num = self.shot_iter_num - 1

        # update full_frame_path with iteration number
        self.full_frame_path = self.full_frame_path_no_ver.replace(
            "$$", str(self.shot_iter_num).zfill(2))

    def create_folder(self, ipt_str):
        if not os.path.exists(ipt_str):
            os.mkdir(ipt_str)
            self.print_info("Created directory " + ipt_str)

    def create_output_folder(self):

        # if job is active and read-only is enabled, create folders
        if self.active:
            self.create_folder(self.frame_render_folder.replace(
                "$$", str(self.shot_iter_num).zfill(2)))

    def read_job(self, job_nr):
        # check if job is active, otherwise jump to next job
        self.active = self.jobs_table[job_nr][1]
        if self.active is None or self.active == '' or self.active == 0:
            self.active = False
            self.cpu_act = False
            self.gpu_act = False
            self.animation_denoise = False
            return
        else:
            self.active = self.tobool(self.active)

        self.hq = self.tobool(self.jobs_table[job_nr][15])
        # check if highquality enabled, otherwise use lowquality settings
        if self.hq:
            self.resolution_scale = 100
            self.framestep = 1
            self.border = False
            self.samples = self.jobs_table[job_nr][8]
        else:
            self.border = True
            if self.preview_samples_active:
                self.samples = self.preview_samples
            else:
                self.samples = self.jobs_table[job_nr][8]

            if self.preview_framestep_active:
                self.framestep = self.preview_framestep
            else:
                self.framestep = 1
            if self.preview_res_active:
                self.resolution_scale = self.preview_res
            else:
                self.resolution_scale = 100

        self.cycles = self.tobool(self.jobs_table[job_nr][10])

        self.blendfilepath = self.jobs_table[job_nr][2].replace(
            "\\", "/").replace('"', '').replace("'", '')  # command
        self.active_camera = self.jobs_table[job_nr][3]  # done
        self.startframe = self.jobs_table[job_nr][4]  # command
        self.endframe = self.jobs_table[job_nr][5]  # command
        self.x_res = self.jobs_table[job_nr][6]
        self.y_res = self.jobs_table[job_nr][7]
        self.file_format = self.jobs_table[job_nr][9]  # command
        # convert file format:
        if self.file_format == "exr":
            self.file_format_upper = "OPEN_EXR_MULTILAYER"
        else:
            self.file_format_upper = self.file_format.upper()

        self.cpu_act = self.tobool(self.jobs_table[job_nr][11])  # done
        self.gpu_act = self.tobool(self.jobs_table[job_nr][12])  # done
        self.motion_blur = self.tobool(self.jobs_table[job_nr][13])  # done
        self.new_version = self.tobool(self.jobs_table[job_nr][14])
        self.animation_denoise = self.tobool(
            self.jobs_table[job_nr][16])
        self.denoise = self.tobool(self.jobs_table[job_nr][17])
        if self.blendfilepath[1] == ":":
            self.blendpath = self.blendfilepath
        else:
            self.blendpath = self.blendfolder + self.blendfilepath
        self.scene = self.jobs_table[job_nr][18]
        # remove empty elements
        self.view_layer = self.jobs_table[job_nr][19].replace(
            ", ", ",").split(",")
        self.view_layer = [
            x for x in self.view_layer if x]

        # If Eevee activated, disable according properties:
        if not self.cycles:
            self.animation_denoise = False
            self.gpu_act = True
            self.cpu_act = False
            self.denoise = False

        self.get_shotname()
        self.get_frame_path()
        self.create_output_folder()

    def render_job(self, device):
        inlinepython = "import sys ; sys.path.append('{}util') ; import rr_renderscript ; rr_renderscript.set_settings('{}', '{}', '{}', {}, '{}', '{}', {}, {}, {}, {}, '{}', {}, {}, {}, '{}', {}, {})".format(
            self.currentpath,
            self.currentpath,
            self.active_camera,
            device,
            self.motion_blur,
            self.x_res,
            self.y_res,
            self.resolution_scale,
            self.animation_denoise,
            self.denoise,
            self.new_version,
            self.samples,
            self.framestep,
            self.cycles,
            self.border,
            self.scene,
            self.view_layer,
            self.add_on_list)

        # print(inlinepython)

        if self.scene != "":
            scene_sub_command_string = " -S " + self.scene
        else:
            scene_sub_command_string = ""

        # if end frame empty, render single frame
        if self.endframe == "" and self.startframe == "":
            render_frame_command = " -a "
        elif self.endframe == "" and self.startframe != "":
            render_frame_command = " -f " + str(self.startframe)
        else:
            render_frame_command = " -s " + \
                str(self.startframe) + " -e " + str(self.endframe) + " -a "

        command_string = ('"' + self.blenderpath + '"' +
                          ' -b ' + '"' + self.blendpath + '"' +
                          scene_sub_command_string +
                          ' -o ' + '"' + self.full_frame_path + '"' +
                          " --python-expr " + '"' + inlinepython + '"' +
                          " -F " + self.file_format_upper +
                          render_frame_command)
        # print(command_string)

        self.print_info("Rendering {} on {}".format(self.shotname +
                                                    str(self.shot_iter_num), device.upper()))
        if "win" in sys.platform:
            return subprocess.Popen(command_string, creationflags=CREATE_NEW_CONSOLE)
        elif "linux" in sys.platform:
            return subprocess.Popen(command_string, shell=True)

    def denoise_job(self, job_nr):
        inlinepython_denoise = "import sys ; sys.path.append('{}util') ; import rr_denoisescript ; rr_denoisescript.denoise_folder_explicit('{}', '{}', {}, {})".format(
            self.currentpath,
            self.currentpath,
            self.frame_render_folder.replace(
                "$$", str(self.shot_iter_num).zfill(2)),
            self.startframe,
            self.endframe
        )
        command_string_denoise = (self.blenderpath + ' -b ' +
                                  ' --python-expr ' + '"' + inlinepython_denoise + '"')
        self.print_info("Denoising " + self.shotname + str(self.shot_iter_num))
        if "win" in sys.platform:
            return subprocess.Popen(command_string_denoise, creationflags=CREATE_NEW_CONSOLE)
        elif "linux" in sys.platform:
            return subprocess.Popen(command_string_denoise, shell=True)

    def save_previous_job_data(self):
        self.active_old = self.active
        self.startframe_old = self.startframe
        self.endframe_old = self.endframe
        self.frame_path_old = self.frame_render_folder
        self.file_format_old = self.file_format
        self.full_frame_path_old = self.full_frame_path
        self.shot_iteration_number_old = self.shot_iter_num
        self.animation_denoise_old = self.animation_denoise

    def check_file(self, ipt_str):
        if os.path.exists(ipt_str):
            if os.path.getsize(ipt_str) > 100:
                return True
        return False

    def check_renders(self):
        if self.active_old:
            self.read_errors()
            # if still image
            if self.startframe == "" and self.endframe == "":
                self.print_info(
                    "If you give me start frame and end frame, I can check if all the frames are rendered!")

            elif self.endframe_old == "":
                searchrange = range(int(self.startframe_old),
                                    int(self.startframe_old) + 1)
            # if animation
            else:
                searchrange = range(int(self.startframe_old),
                                    int(self.endframe_old) + 1)

            if self.animation_denoise_old:
                self.full_frame_path_old = "_dn/".join(
                    self.full_frame_path_old.rsplit("/", 1))

            for frame in searchrange:
                check_path = self.full_frame_path_old.replace(
                    "####",
                    str(frame).zfill(4))
                if not self.check_file(check_path):
                    self.print_warning_noinput(" I checked {} and saw that something didn't work. Try rendering it again!".format(
                        self.full_frame_path_old).replace("####", str(frame).zfill(4)))
                    return None

    def delete_empty_folders(self, ipt_dir):
        if ipt_dir[-1:] != "/":
            ipt_dir = ipt_dir + "/"
        print(ipt_dir)
        directories_files = os.listdir(ipt_dir)
        print(directories_files)
        for directory in directories_files:
            #check if is dir
            abs_dir = ipt_dir + directory
            if os.path.isdir(abs_dir):
                #check if is empty
                if not os.listdir(abs_dir):
                    os.rmdir(abs_dir)
                    self.print_info("Deleted /" + directory + "/")

    def start_generate(self):
        for job in range(1, len(self.jobs_table)):
            self.read_job(job)
            # check if blend file exists
            if not os.path.exists(self.blendpath):
                self.print_warning_noinput(
                    f"I didn't find {self.blendpath}. Please check if it exists!")
                # set self.active_old so that there is not gonna be a check of this render
                self.active_old = False
                continue

            if self.active and self.cpu_act:
                self.thread_cpu = self.render_job("cpu")

            if self.thread_gpu_an_dn is not None:
                self.thread_gpu_an_dn.wait(1048574)

            if hasattr(self, "active_old"):
                self.check_renders()

            # sleep, to avoid simultanous start, so both render first frame
            sleep(0.1)
            if self.active and self.gpu_act:
                self.thread_gpu = self.render_job("gpu")

            if self.thread_cpu is not None:
                self.thread_cpu.wait(1048574)

            if self.thread_gpu is not None:
                self.thread_gpu.wait(1048574)

            if self.active and self.animation_denoise:
                self.thread_gpu_an_dn = self.denoise_job(job)

            self.save_previous_job_data()

        # wait if an denoising is still running
        if self.thread_gpu_an_dn is not None:
            self.thread_gpu_an_dn.wait(1048574)

        self.check_renders()


if __name__ == "__main__":
    try:
        jobs_obj = jobs()
        jobs_obj.start_generate()
        jobs_obj.delete_empty_folders(jobs_obj.renderpath)
        jobs_obj.print_info_input("I'm done here. Press enter and I'm gone!")
        print(rs.all)
    except KeyboardInterrupt:
        jobs_obj.print_info("Okay, I understood!")
        if jobs_obj.thread_cpu is not None:
            jobs_obj.thread_cpu.terminate()
        if jobs_obj.thread_gpu is not None:
            jobs_obj.thread_gpu.terminate()
        if jobs_obj.thread_gpu_an_dn is not None:
            jobs_obj.thread_gpu_an_dn.terminate()
