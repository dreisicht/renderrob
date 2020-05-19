
import bpy  # pylint: disable=import-error
import time
import sys
import os
import rr_c_image  # pylint: disable=import-error
from ast import literal_eval
from multiprocessing import cpu_count
from colorama import Fore, Back, Style, init


user_settings_folder = str(__file__).replace("\\", "/").replace("/util/rr_renderscript.py", "/user")
print(user_settings_folder)
sys.path.append(user_settings_folder)
import rr_user_commands

init(convert=True)

scriptpath_glob = ""

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# red = hex_to_rgb("980030")
# green = hex_to_rgb("499a6c")
# yellow = hex_to_rgb("ffd966")
# grey = hex_to_rgb("999999")
# light_blue = hex_to_rgb("78909c")
# dark_blue = hex_to_rgb("45818e")
# lighter_stone = hex_to_rgb("242a2d")
# dark_stone = hex_to_rgb("22282b")

# bg.red = Style(RgbBg(red[0], red[1], red[2]))
# bg.green = Style(RgbBg(green[0], green[1], green[2]))
# bg.yellow = Style(RgbBg(yellow[0], yellow[1], yellow[2]))
# bg.grey = Style(RgbBg(grey[0], grey[1], grey[2]))
# bg.light_blue = Style(RgbBg(light_blue[0], light_blue[1], light_blue[2]))
# bg.dark_blue = Style(RgbBg(dark_blue[0], dark_blue[1], dark_blue[2]))
# bg.lighter_stone = Style(RgbBg(lighter_stone[0], lighter_stone[1], lighter_stone[2]))
# bg.dark_stone = Style(RgbBg(dark_stone[0], dark_stone[1], dark_stone[2]))


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
        print("Error")
        # raise TypeError


# def inexclude_collection(collection_names, exclude, view_layer_data, parent=""):
#     #### FUNCTION CURRENTLY NOT BEING USED
#     # check if first function being called first time

#     if parent == "":
#         counter = 0
#         for name in collection_names:
#             if name == "":
#                 collection_names.pop(counter)
#             counter += 1
#         parent_collection = view_layer_data.layer_collection
#         # if function being called first time, reset number of changed
#     else:
#         parent_collection = parent

#     # iterate through immediate children of collection
#     for collection in parent_collection.children:
#         # check name
#         if collection.name in collection_names:
#             collection.exclude = exclude
#             collection_names.pop(collection_names.index(collection.name))
#         # check if has children
#         if len(collection.children) > 0:
#             inexclude_collection(
#                 collection_names, exclude, view_layer_data, parent=collection)
#         else:
#             continue
#     # IQ 300 move here: collections get pop-ed above, so the rest, that is not found, is printed here
#     if parent == "" and len(collection_names) > 0:
#         print_warning("I couldn't find collection {}!".format(
#             " and ".join(collection_names)))


def print_error(ipt_str):
    ipt_str = str(ipt_str)
    print(Back.RED, Fore.WHITE, end="")
    print("[ERROR] " + ipt_str + " Exiting in 3 seconds.")
    print(Style.RESET_ALL, end="")
    write_cache("[ERROR]" + ipt_str)
    time.sleep(3)
    sys.exit()


def print_warning(ipt_str):
    ipt_str = str(ipt_str)
    print(Back.YELLOW, Fore.BLACK, end="")
    print("[WARNING] " + ipt_str)
    print(Style.RESET_ALL, end="")
    write_cache("[WARNING]" + ipt_str)
    time.sleep(1)


def print_info_input(ipt_str):
    ipt_str = str(ipt_str)
    print(Back.CYAN, Fore.BLACK, end="")
    input("[INFO] " + ipt_str)
    print(Style.RESET_ALL, end="")
    # write_cache("[INFO]" + ipt_str)


def print_info(ipt_str):
    ipt_str = str(ipt_str)
    print(Back.CYAN, Fore.BLACK + "[INFO] " + ipt_str + Style.RESET_ALL)
    # write_cache("[INFO]" + ipt_str)


def write_cache(ipt_str):
    global scriptpath_glob
    cachefilepath = scriptpath_glob + "util/ERRORCACHE"
    try:
        f = open(cachefilepath, "a")
    except PermissionError:
        time.sleep(0.1)
        f = open(cachefilepath, "a")
    finally:
        time.sleep(0.1)
    f.write(ipt_str + "\n")
    f.close()


def set_settings(scriptpath,
                 camera,
                 device,
                 mb,
                 xres,
                 yres,
                 percres,
                 an_denoise,
                 denoise,
                 overwrite,
                 placeholder,
                 samples,
                 frame_step,
                 cycles,
                 border,
                 scene,
                 view_layer_names,
                 add_on_list):
    
    global scriptpath_glob
    scriptpath_glob = scriptpath
    
    try:
        print_info("Render Rob here. I'm starting to make my changes in your Blender file!")

    
        if scene == "" and len(bpy.data.scenes) > 1:
            print_warning(
                "There are more than one scenes, but you didn't tell me which scene to render! So I am rendering the last used scene.")
            current_scene_data = bpy.context.scene
        elif len(bpy.data.scenes) == 1:
            current_scene_data = bpy.data.scenes[0]
        else:
            try:
                current_scene_data = bpy.data.scenes[scene]
            except KeyError:
                print_error("Scene {} not found!".format(scene))

        # first we deactivate all View Layers:
        for view_layer in current_scene_data.view_layers:
            view_layer.use = False

        if view_layer_names == []:
            # if only one view_layer in scene
            if len(current_scene_data.view_layers) == 1:
                view_layer_data = current_scene_data.view_layers[0]
            else: 
                print_info("I'm rendering every active View Layer! You can specify the View Layer to be rendered in the sheet!")
                view_layer_data = current_scene_data.view_layers
        # if only one view_layer given
        elif len(view_layer_names) == 1 and view_layer_names != []:
            # if only one view_layer in scene
            if len(current_scene_data.view_layers) == 1:
                view_layer_data = current_scene_data.view_layers[0]
            # if more than one view layer in scene
            else:
                try:
                    view_layer_data = current_scene_data.view_layers[view_layer_names[0]]
                except KeyError:
                    print_error("View Layer {} not found. Please check the name in the sheet!".format(view_layer_names[0])) # TODO: test
        # if more than one view_layer given:
        elif len(view_layer_names) > 1:
            # print("A3")
            if len(current_scene_data.view_layers) < len(view_layer_names):
                print_error("You gave me more View Layers given than existing! ({})".format(", ".join(view_layer_names)))
            else:
                view_layer_data = []
                
                for vl in view_layer_names:
                    view_layer_data.append(current_scene_data.view_layers[vl])
        else:
            print_error("Unexpected ViewLayer Error.")

        if type(view_layer_data) is bpy.types.bpy_prop_collection or type(view_layer_data) is list:
            for view_layer in view_layer_data:
                view_layer.use = True
        elif type(view_layer_data) is bpy.types.ViewLayer:
            view_layer_data.use = True
        else:
            print_error("Unexpected ViewLayer Error.")

        # activate add-ons:
        for add_on in add_on_list:
            print_info(str(add_on))
            try:
                bpy.ops.preferences.addon_enable(module=add_on)
                print_info("I activated the addon {}.".format(add_on))
            except:
                print_error("I Couldn't find the addon {}. Maybe it's not installed yet?".format(add_on))

        current_scene_render = current_scene_data.render

        try:
            if camera != '':
                current_scene_data.camera = bpy.data.objects[camera]
        except KeyError:
            print_error("I didn't find the camera called {}.".format(camera))

        # disable render border
        current_scene_render.use_border = border
        


        if cycles is False:
            if samples != "":
                current_scene_data.eevee.taa_render_samples = int(samples)
            current_scene_render.engine = 'BLENDER_EEVEE'
            current_scene_data.eevee.use_motion_blur = mb
        elif cycles:
            current_scene_render.engine = 'CYCLES'
            if samples != "":
                current_scene_data.cycles.samples = int(samples)

            # cpu
            if device == "cpu":
                current_scene_render.threads_mode = 'FIXED'
                current_scene_render.threads = cpu_count() - 2
                current_scene_data.cycles.device = 'CPU'
                current_scene_render.tile_x = 64
                current_scene_render.tile_y = 64

            # gpu
            if device == "gpu":
                cycles_pref = bpy.context.preferences.addons['cycles'].preferences
                cycles_pref.get_devices()
                cycles_pref.compute_device_type = 'CUDA'

                current_scene_data.cycles.device = 'GPU'

                for device in cycles_pref.devices:
                    if "GeForce" in str(device.name):
                        device.use = True
                        print_info("Using device" + str(device.name))
                    if "GHz" in str(device.name):
                        device.use = False

                    # print_info(device.name, device.use)

                current_scene_render.tile_x = 256
                current_scene_render.tile_y = 256

            # motion blur
            current_scene_render.use_motion_blur = mb

            # denoising data
            if type(view_layer_data) is bpy.types.bpy_prop_collection or type(view_layer_data) is list:
                for view_layer in view_layer_data:

                    view_layer.cycles.denoising_store_passes = an_denoise
                    view_layer.cycles.use_denoising = denoise
            elif type(view_layer_data) is bpy.types.ViewLayer:
                view_layer_data.cycles.denoising_store_passes = an_denoise
                view_layer_data.cycles.use_denoising = denoise
            else:
                print_error("Denoising Handling went wrong.")

            # disable compositing if animation_denoising
            current_scene_render.use_compositing = not an_denoise
            current_scene_data.use_nodes = not an_denoise
            current_scene_data.cycles.use_animated_seed = an_denoise

        print_info("Rendering on " + str(device))
        # output settings
        if xres != "":
            
            current_scene_render.resolution_x = int(xres)
        if yres != "":
            current_scene_render.resolution_y = int(yres)
        current_scene_render.resolution_percentage = percres

        # overwrite, placeholder
        current_scene_render.use_overwrite = overwrite
        current_scene_render.use_placeholder = placeholder

        # n-th frame
        current_scene_data.frame_step = frame_step

        print_info("Done making the changes in your Blender file.")
        time.sleep(2)
    except Exception as e:
        print_info(e)
        write_cache("[ERROR]" + e)
        print_info("I'm out!")
        time.sleep(2)
        sys.exit()
        









# set_settings('Camera_top', 'cpu', True, 1920, 1080, 25, True, False, False, True, 4, 1, True, True, ['objects 1', 'objects 2'], ['objects'], 'Scene', ['View Layer'], ['animation_nodes', 'asdf'])

# set_settings('Camera_top', 'gpu', True, 1920, 1080, 25, True, False, False, True, 4, 1, True, True, [''], [''], '', [''], ['animation_nodes', 'asdf'])
