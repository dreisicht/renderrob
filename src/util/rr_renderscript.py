import bpy  # pylint: disable=import-error
import time
import sys
from ast import literal_eval
from colorama import Fore, Back, Style, init

sys.path.append(str(__file__)[0:-18].replace("\\", "/"))
# import rr_user_commands
init(convert=True)
# bpsc = bpy.context.scene
# bprn = bpsc.render


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


def inexclude_collection(collection_names, exclude, view_layer_data, parent=""):
    # check if first function being called first time

    if parent == "":
        counter = 0
        for name in collection_names:
            if name == "":
                collection_names.pop(counter)
            counter += 1
        parent_collection = view_layer_data.layer_collection
        # if function being called first time, reset number of changed
    else:
        parent_collection = parent

    # iterate through immediate children of collection
    for collection in parent_collection.children:
        # check name
        if collection.name in collection_names:
            collection.exclude = exclude
            collection_names.pop(collection_names.index(collection.name))
        # check if has children
        if len(collection.children) > 0:
            inexclude_collection(
                collection_names, exclude, view_layer_data, parent=collection)
        else:
            continue
    # IQ 300 move here: collections get pop-ed above, so the rest, that is not found, is printed here
    if parent == "" and len(collection_names) > 0:
        print_warning("I couldn't find collection {}!".format(
            " and ".join(collection_names)))

def print_error(ipt_str):
    print(Back.RED, Fore.BLACK)
    input("[ERROR] " + ipt_str + " Press any key to exit.")
    print(Style.RESET_ALL)
    quit()

def print_warning(ipt_str):
    print(Back.YELLOW, Fore.BLACK)
    input("[WARNING] " + ipt_str + " Press any key to continue.")
    print(Style.RESET_ALL)

def print_info_input(ipt_str):
    print(Back.CYAN, Fore.BLACK)
    input("[INFO] " + ipt_str)
    print(Style.RESET_ALL)
    
    
def print_info(ipt_str):
    print(Back.CYAN + "[INFO] " + ipt_str + Style.RESET_ALL)


def set_settings(camera,
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
                 activate_collections,
                 deactivate_collections,
                 scene,
                 view_layer_names):
    print_info("Render Rob here. I'm starting to make my changes in your Blender file!")

    if scene == "" and len(bpy.data.scenes) > 1:
        print_warning(
            "There are more than one scenes, but you didn't tell me which scene to render! So I render the last used scene.")
        # time.sleep(10)
    current_scene_data = bpy.context.scene

    # if no view layer given
    view_layer_names = literal_eval(view_layer_names)
    if len(view_layer_names) == 0:
        # if only one view_layer in scene
        if len(current_scene_data.view_layers) == 1:
            view_layer_data = current_scene_data.view_layers[0]
        else: 
            print("I'm rendering every active View Layer! You can specify the View Layer to be rendered in the sheet!")
            view_layer_data = current_scene_data.view_layers
    # if only one view_layer given
    elif len(view_layer_names) == 1 and view_layer_names[0] != "":
        # if only one view_layer in scene
        if len(current_scene_data.view_layers) == 1:
            view_layer_data = current_scene_data.view_layers[0]
        # if more than one view layer in scene
        else:
            try:
                view_layer_data = current_scene_data.view_layers[view_layer_names[0]]
            except KeyError:
                print_error("View Layer not found. Please check the name in the sheet!")
    # if more than one view_layer given:
    else:
        if len(current_scene_data.view_layers) < len(view_layer_names):
            print_error("You gave me more View Layers given than existing")
        else:
            view_layer_data = []
            for vl in view_layer_names:
                view_layer_data.append(current_scene_data.view_layers[vl])

    current_scene_render = current_scene_data.render

    try:
        if camera != '':
            current_scene_data.camera = bpy.data.objects[camera]
    except KeyError:
        print_warning("I didn't find the camera called {}.".format(camera))
        time.sleep(10)

    try:
        if type(view_layer_data) is bpy.types.bpy_prop_collection:
            for view_layer in view_layer_data:
                inexclude_collection(deactivate_collections, True, view_layer)
                inexclude_collection(activate_collections, False, view_layer)
        elif type(view_layer_data) is bpy.types.ViewLayer:
            inexclude_collection(deactivate_collections, True, view_layer_data)
            inexclude_collection(activate_collections, False, view_layer_data)

        # disable render border
        current_scene_render.use_border = border

        if cycles is False:
            current_scene_render.engine = 'BLENDER_EEVEE'
            current_scene_data.eevee.taa_render_samples = samples
            current_scene_data.eevee.use_motion_blur = mb
        elif cycles:
            current_scene_render.engine = 'CYCLES'
            current_scene_data.cycles.samples = samples

            # cpu
            if device == "cpu":
                current_scene_render.threads_mode = 'FIXED'
                current_scene_render.threads = 22
                current_scene_data.cycles.device = 'CPU'
                current_scene_render.tile_x = 32
                current_scene_render.tile_y = 32

            # gpu
            if device == "gpu":
                cycles_pref = bpy.context.preferences.addons['cycles'].preferences
                cycles_pref.get_devices()
                cycles_pref.compute_device_type = 'CUDA'

                current_scene_data.cycles.device = 'GPU'
                # print(bpsc.cycles.device)
                # bpy.ops.render.render(True)

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
            if type(view_layer_data) is bpy.types.bpy_prop_collection:
                for view_layer in view_layer_data:
                    view_layer.cycles.denoising_store_passes = an_denoise
                    view_layer.cycles.use_denoising = denoise
            elif type(view_layer_data) is bpy.types.ViewLayer:
                view_layer.cycles.denoising_store_passes = an_denoise
                view_layer.cycles.use_denoising = denoise

            # disable compositing if animation_denoising
            current_scene_render.use_compositing = not an_denoise
            current_scene_data.use_nodes = not an_denoise
            current_scene_data.cycles.use_animated_seed = an_denoise

        print_info("Rendering on " + str(device))
        # output settings
        current_scene_render.resolution_x = xres
        current_scene_render.resolution_y = yres
        current_scene_render.resolution_percentage = percres

        # overwrite, placeholder
        current_scene_render.use_overwrite = overwrite
        current_scene_render.use_placeholder = placeholder
        # print(current_scene_render.use_placeholder)

        # n-th frame
        current_scene_data.frame_step = frame_step

        print_info("Done making the changes in your Blender file.")
    except KeyError:
        print_error("Sorry, unknown error.")
