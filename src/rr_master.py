import os
import sys
import glob
import xlrd
import threading
import subprocess
from time import sleep
from datetime import datetime
# from colorama import Fore, Back, Style, init
from sty import fg, bg, ef, rs, Style, RgbBg
import sty
from rr_gspread import query_sheet
from subprocess import Popen, CREATE_NEW_CONSOLE
import rr_image


class jobs(object):
    def __init__(self):
        self.print_info("Hello from Render Rob! I'm glad to help you!")
        self.currentpath = os.path.dirname(
            sys.argv[0]).replace("\\", "/") + "/"
        # print(glob.glob(self.currentpath + "*.xlsx"))
        excel_file = glob.glob(self.currentpath + "*.xlsx")
        if len(excel_file) > 0:
            self.jobs_table, global_set = self.rr_read_excel(
                excel_file[0].replace("\\", "/"))
            self.print_info("I found an Excel file. I'm gonna use that one!")
            # print(self.jobs_table, global_set)
        else:
            if not glob.glob(self.currentpath + "/key/*.json"):
                self.print_error("I didn't find either an .xlsx file or a .json key. Please provide one of the two!")
            try:
                self.print_info("I'm gonna go and get the data from Google Sheets.")
                self.jobs_table, global_set = query_sheet()
                self.print_info("I successfully downloaded the data from Google Sheets.")
            except:
                self.print_error("Couldn't get the data from Google Sheets. Maybe check your json key!")
            # print(self.jobs_table, global_set)

        self.blenderpath = global_set[0][1].replace("\\", "/")
        self.renderpath = self.path_process(global_set[1][1])
        self.blendfolder = self.path_process(global_set[2][1])
        self.add_on_list = global_set[6][1].replace(", ", ",").split(",")
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
        bg.yellow = Style(RgbBg(self.yellow[0], self.yellow[1], self.yellow[2]))
        bg.grey = Style(RgbBg(self.grey[0], self.grey[1], self.grey[2]))
        bg.light_blue = Style(RgbBg(self.light_blue[0], self.light_blue[1], self.light_blue[2]))
        bg.dark_blue = Style(RgbBg(self.dark_blue[0], self.dark_blue[1], self.dark_blue[2]))
        bg.lighter_stone = Style(RgbBg(self.lighter_stone[0], self.lighter_stone[1], self.lighter_stone[2]))
        bg.dark_stone = Style(RgbBg(self.dark_stone[0], self.dark_stone[1], self.dark_stone[2]))

        # check if blender path is filled out correctly
        if self.blenderpath == "C:/Path/To/Blender.exe":
            self.print_error("Please fill the path to blender under globals!")
            quit()
        elif not os.path.isfile(self.blenderpath[1:-1]):
            self.print_error("I couldn't find the Blender folder. Perhaps a spelling mistake?")
            quit()

        # check if render path is filled out correctly
        if self.renderpath == "C:/Path/To/My/Renders/":
            self.print_error(
                "Please fill the path to you render folder under globals!")
            quit()
        elif not os.path.exists(self.renderpath):
            self.print_error("I couldn't find the render output folder. Perhaps a spelling mistake?")
            quit()
        
        if not os.path.exists(self.blendfolder):
            self.print_warning("I couldn't find the .blend file folder. Perhaps a spelling mistake?")
            # quit()

        self.preview_res = global_set[3][1]
        self.preview_res_active = self.tobool(global_set[3][2])

        self.preview_samples = global_set[4][1]
        self.preview_samples_active = self.tobool(global_set[4][2])

        self.preview_framestep = global_set[5][1]
        self.preview_framestep_active = self.tobool(global_set[5][2])

        self.shot_iteration_number = 1

        self.thread_cpu = None
        self.thread_gpu = None
        self.thread_gpu_an_dn = None

    def rr_read_excel(self, path_sheet):
        wb = xlrd.open_workbook(path_sheet)
        jobs_sheet = wb.sheet_by_index(0)
        global_sheet = wb.sheet_by_index(1)

        return self.fill_array(jobs_sheet), self.fill_array(global_sheet)

    # print methods
    @staticmethod
    def print_error(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.red + fg.white + time_current + "[ERROR] " + ipt_str + " Press Enter to exit." + rs.all)
        quit()
        
    @staticmethod
    def hex_to_rgb(h):
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def print_warning(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.yellow + fg.black + time_current + "[WARNING] " + ipt_str + " Press Enter to continue." + rs.all)

    @staticmethod
    def print_info_input(ipt_str):
        time_current = "[{}]".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        input(bg.dark_blue + fg.white + time_current + "[INFO] " + ipt_str + " Press Enter to continue." + rs.all)

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
                # raise TypeError
        elif type(bool_val) == int:
            if bool_val == 0:
                return False
            elif bool_val == 1:
                return True
        else:
            print("Bool Error")
            # raise TypeError

    def get_shotname(self):
        # preview or hq suffix
        if self.hq:
            self.quality_state_string = "hq"
        else:
            self.quality_state_string = "preview"

        # get blender file name without .blend

        filename = self.blendpath.split("/")[-1][:-6]
        self.shotname = (filename + "-" +
                         self.active_camera + "-" +
                         str(self.startframe) + "-" +
                         str(self.endframe) + "-" +
                         str(self.scene) + "-" +
                         self.quality_state_string + "-v")
        
        # get iteration number
        if self.endframe == "":
            self.frame_path = self.renderpath + "stills/"
            self.shot_iteration_number = 1
            while os.path.exists(self.frame_path + self.shotname + str(self.shot_iteration_number).zfill(2) + "-" + str(self.startframe).zfill(4) + "." + self.file_format):  # TODO
                self.print_info(self.shot_iteration_number)
                self.shot_iteration_number = self.shot_iteration_number + 1
                
        else:
            self.frame_path = self.renderpath + self.shotname
            self.shot_iteration_number = 1
            while os.path.exists(self.frame_path + str(self.shot_iteration_number).zfill(2)):
                self.shot_iteration_number = self.shot_iteration_number + 1

        # print(self.frame_path + str(self.shot_iteration_number).zfill(2))

        # if still frame rendering, create stills folder
        if self.endframe == "":
            if not os.path.exists(self.frame_path):
                os.mkdir(self.frame_path)
                self.print_info("I created directory " + self.frame_path)

            self.full_frame_path = (self.frame_path + self.shotname + str(self.shot_iteration_number).zfill(2) + "-" + "####." + self.file_format) # TODO
            self.print_info(self.full_frame_path)

        # if overwrite active, get to the folder with the highest iteration number
        else:
            if self.active:
                if self.overwrite and self.shot_iteration_number > 1:
                    self.shot_iteration_number = self.shot_iteration_number - 1
                else:
                    print("[{}]".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                          "I created directory " + self.frame_path +
                          str(self.shot_iteration_number).zfill(2))
                    os.mkdir(self.frame_path +
                             str(self.shot_iteration_number).zfill(2))

            # if animation denoise active, create folder
            if self.animation_denoise and self.active:
                denoise_folder = self.frame_path + \
                    str(self.shot_iteration_number).zfill(2) + "_dn"
                if not os.path.exists(denoise_folder):
                    os.mkdir(denoise_folder)
                    print("[{}]".format(datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')), "I created directory " + denoise_folder)

            # get path of the frames
            self.full_frame_path = (self.frame_path +
                                    str(self.shot_iteration_number).zfill(2) + "/"
                                    + self.shotname + "-" + "####." + self.file_format)

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

        self.hq = self.tobool(self.jobs_table[job_nr][16])
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
        self.overwrite = not self.tobool(self.jobs_table[job_nr][14])
        self.placeholder = self.tobool(self.jobs_table[job_nr][15])
        self.animation_denoise = self.tobool(
            self.jobs_table[job_nr][17])
        self.denoise = self.tobool(self.jobs_table[job_nr][18])
        if self.blendfilepath[1] == ":":
            self.blendpath = self.blendfilepath
        else:
            self.blendpath = self.blendfolder + self.blendfilepath
        # print(self.currentpath)
        self.scene = self.jobs_table[job_nr][19]
        self.activate_collections = self.jobs_table[job_nr][20].replace(
            ", ", ",").split(",")
        # remove empty elements
        self.activate_collections = [x for x in self.activate_collections if x]

        self.deactivate_collections = self.jobs_table[job_nr][21].replace(
            ", ", ",").split(",")
        self.deactivate_collections = [x for x in self.deactivate_collections if x]
        self.view_layer = self.jobs_table[job_nr][20].replace(
            ", ", ",").split(",")
        self.view_layer = [
            x for x in self.view_layer if x]
        self.get_shotname()

    def render_job(self, device):
        inlinepython = "import sys ; sys.path.append('{}util') ; import rr_renderscript ; rr_renderscript.set_settings('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, '{}', {}, {})".format(
            self.currentpath,
            self.active_camera,
            device,
            self.motion_blur,
            self.x_res,
            self.y_res,
            self.resolution_scale,
            self.animation_denoise,
            self.denoise,
            self.overwrite,
            self.placeholder,
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
        if self.endframe == "":
            render_frame_command = " -f " + str(self.startframe) 
        else:
            render_frame_command = " -s " + \
                str(self.startframe) + " -e " + str(self.endframe) + " -a "

        command_string = (self.blenderpath +
                          ' -b ' + self.blendpath +
                          scene_sub_command_string +
                          ' -o ' + self.full_frame_path +
                          " --python-expr " + '"' + inlinepython + '"' +
                          " -F " + self.file_format_upper +
                          render_frame_command)
        # print(command_string)
        # return "None"
        print("[{}]".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
              "Rendering {} on {}".format(self.shotname +
                                          str(self.shot_iteration_number), device.upper()))
        return subprocess.Popen(command_string, creationflags=CREATE_NEW_CONSOLE)
        # subprocess.run(command_string)

    def denoise_job(self, job_nr):
        inlinepython_denoise = "import sys ; sys.path.append('{}util') ; import rr_denoisescript ; rr_denoisescript.denoise_folder('{}/', {}, {})".format(
            self.currentpath,
            self.frame_path + str(self.shot_iteration_number).zfill(2),
            self.startframe,
            self.endframe
        )
        command_string_denoise = (self.blenderpath + ' -b ' +
                                  ' --python-expr ' + '"' + inlinepython_denoise + '"')
        # print(command_string_denoise)
        print("[{}]".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
              "Denoising", self.shotname + str(self.shot_iteration_number))
        # return "None"
        return subprocess.Popen(command_string_denoise, creationflags=CREATE_NEW_CONSOLE)

    def start_generate(self):
        for job in range(1, len(self.jobs_table)):
            self.read_job(job)

            if self.active and self.cpu_act:
                self.thread_cpu = self.render_job("cpu")

            if self.thread_gpu_an_dn is not None:
                self.thread_gpu_an_dn._wait(1048574)

            # sleep, to avoid simultanous start, so both render first frame
            sleep(0.1)
            if self.active and self.gpu_act:
                self.thread_gpu = self.render_job("gpu")

            if self.thread_cpu is not None:
                self.thread_cpu._wait(1048574)
            if self.thread_gpu is not None:
                self.thread_gpu._wait(1048574)

            if self.active and self.animation_denoise:
                self.thread_gpu_an_dn = self.denoise_job(job)

        # wait if an denoising is still running
        if self.thread_gpu_an_dn is not None:
            self.thread_gpu_an_dn._wait(1048574)


# initialize colorama
# init(convert=True)
jobs_obj = jobs()
jobs_obj.start_generate()
# print("Window closing in 10 minutes.")
byebyestr = "[{}] ".format(datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')) + "I'm done here. Press enter and I'm gone!"
print(fg.white, bg.dark_blue)
input(byebyestr)
print(rs.all)
