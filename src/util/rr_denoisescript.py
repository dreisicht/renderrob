import bpy  # pylint: disable=import-error
import os
import glob
import time
import sys


def write_cache(scriptpath, ipt_str):
    cachefilepath = scriptpath + "util/ERRORCACHE"
    # print(cachefilepath)
    try:
        f = open(cachefilepath, "a")
    except PermissionError:
        # print("First try failed.")
        time.sleep(0.1)
        f = open(cachefilepath, "a")
    finally:
        # print("caching failed!")
        time.sleep(0.1)
    f.write(ipt_str + "\n")
    f.close()


def denoise_folder_explicit(scriptpath, inputdir, startframe, endframe):
    # inputdir = "D:/3D/Masterarbeit/2d/render/o_08/"
    try:
        outputdir = inputdir[:-1]+"_dn/"
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        # outputdir = "D:/3D/Masterarbeit/2d/render/o_08_dn/"
        os.chdir(inputdir)
        myfiles = (glob.glob("*.exr"))
        print(myfiles)
        for file in myfiles:
            for framenum in range(startframe, endframe + 1):
                if file[-8:-4] == str(framenum).zfill(4):
                    print(inputdir + file + " to " + outputdir + file + "\n")
                    bpy.ops.cycles.denoise_animation(input_filepath=(
                        inputdir + file), output_filepath=(outputdir + file))
        # write_cache("Denoised frames from {} to {}.".format(startframe, endframe))
    except Exception as e:
        write_cache(scriptpath, "[ERROR]" + str(e))
    # time.sleep(10)


def denoise_folder(inputdir):
    outputdir = inputdir[:-1]+"_dn/"
    os.chdir(inputdir)
    myfiles = (glob.glob("*.exr"))
    for file in myfiles:
        print(inputdir + file + " to " + outputdir + file)
        bpy.ops.cycles.denoise_animation(input_filepath=(
            inputdir + file), output_filepath=(outputdir + file))
    # time.sleep(10)


if __name__ == "__main__":
    denoise_folder_explicit(sys.argv[0],
        "C:/Users/peter/Desktop/testproject/render/shot_01-Cam_top-40-43-Sc.001-Vl.002-preview-v02", 40, 41)
