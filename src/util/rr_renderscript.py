import rr_user_commands
import bpy  # pylint: disable=import-error
import time
import sys

sys.path.append(str(__file__)[0:-18].replace("\\", "/"))

# bpsc = bpy.context.scene
# bprn = bpsc.render


def tobool(string):
    if string.upper() == "FALSE":
        return False
    elif string.upper() == "TRUE":
        return True
    else:
        raise TypeError


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
    if parent == "" and len(collection_names) > 0:
        print("ERROR: Couldn't find collection {}!".format(
            " and ".join(collection_names)))
        time.sleep(10)


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
                 view_layer):
    print("____________________ Starting settings ____________________")

    if scene == "":
        current_scene_data = bpy.data.scenes[0]
    else:
        try:
            current_scene_data = bpy.data.scenes[scene]
        except:
            print("Wrong scene name. Please check again!")
            time.sleep(10)

    if view_layer == "":
        view_layer_data = current_scene_data.view_layers[0]
    else:
        try:
            view_layer_data = current_scene_data.view_layers[view_layer]
        except:
            print("Wrong view layer name. Please check again!")
            time.sleep(10)

    current_scene_render = current_scene_data.render

    try:
        if camera != '':
            current_scene_data.camera = bpy.data.objects[camera]
    except KeyError as keyerroridentifier:
        print(keyerroridentifier)
        time.sleep(10)

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
                if "GHz" in str(device.name):
                    device.use = False

                print(device.name, device.use)

            current_scene_render.tile_x = 256
            current_scene_render.tile_y = 256

        # motion blur
        current_scene_render.use_motion_blur = mb

        # denoising data
        view_layer_data.cycles.denoising_store_passes = an_denoise
        view_layer_data.cycles.use_denoising = denoise
        # disable compositing if animation_denoising
        current_scene_render.use_compositing = not an_denoise
        current_scene_data.use_nodes = not an_denoise
        current_scene_data.cycles.use_animated_seed = an_denoise

    print("DEVICE: ", device)
    # output settings
    current_scene_render.resolution_x = xres
    current_scene_render.resolution_y = yres
    current_scene_render.resolution_percentage = percres

    # overwrite, placeholder
    current_scene_render.use_overwrite = overwrite
    current_scene_render.use_placeholder = placeholder

    # n-th frame
    current_scene_data.frame_step = frame_step

    print("____________________ Finished settings ____________________")
    
if __name__ == "__main__":
    set_settings('Camera_top', 'gpu', True, 1920, 1080, 25, True, False, False, True, 4, 1, True, True, [
                                 'objects 1', 'objects 2'], ['objects'], 'Scene.001', 'View Layer.001')


# set_settings('Camera_top', 'gpu', True, 1920, 1080, 10,
#              False, False, False, True, 1, 1, True, True)
