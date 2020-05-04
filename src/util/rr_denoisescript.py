import bpy  # pylint: disable=import-error
import os
import glob


def denoise_folder(inputdir, startframe, endframe):
    searchrange = range(startframe, endframe)
    # inputdir = "D:/3D/Masterarbeit/2d/render/o_08/"
    outputdir = inputdir[:-1]+"_dn/"
    # outputdir = "D:/3D/Masterarbeit/2d/render/o_08_dn/"
    os.chdir(inputdir)
    myfiles = (glob.glob("*.exr"))
    for file in myfiles:
        for framenum in searchrange:
            if file[-8:-4] == str(framenum).zfill(4):
                print(inputdir + file + " to " + outputdir + file)
                bpy.ops.cycles.denoise_animation(input_filepath=(
                    inputdir + file), output_filepath=(outputdir + file))
