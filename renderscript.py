import sys
import time
from multiprocessing import cpu_count

import bpy

import print_utils
import rr_c_image


def set_settings(camera,
                 render_device,
                 motion_blur,
                 xres,
                 yres,
                 percres,
                 an_denoise,
                 denoise,
                 samples,
                 frame_step,
                 cycles,
                 border,
                 scene,
                 view_layer_names,
                 add_on_list):
  """Set the render settings."""
  rr_c_image.draw_image()

  try:
    print_utils.print_info(
        "Render Rob here. I'm starting to make my changes in your Blender file!")

    if scene == "" and len(bpy.data.scenes) > 1:
      print_utils.print_warning(
          "There are more than one scenes, but you didn't tell me which scene to render! So I am"
          " rendering the last used scene.")
      current_scene_data = bpy.context.scene
    elif len(bpy.data.scenes) == 1:
      current_scene_data = bpy.data.scenes[0]
    else:
      try:
        current_scene_data = bpy.data.scenes[scene]
      except KeyError:
        print_utils.print_error(f"Scene {scene} not found!")

    # first we deactivate all View Layers:
    for view_layer in current_scene_data.view_layers:
      view_layer.use = False

    if view_layer_names == []:
      if len(current_scene_data.view_layers) == 1:
        view_layer_data = current_scene_data.view_layers[0]
      else:
        print_utils.print_info(
            "I'm rendering every active View Layer! You can specify the View Layer to be rendered"
            " in the sheet!")
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
          print_utils.print_error(f"View Layer {view_layer_names[0]} not found. Please check the"
                                  " name in the sheet!")
    # if more than one view_layer given:
    elif len(view_layer_names) > 1:
      # print("A3")
      if len(current_scene_data.view_layers) < len(view_layer_names):
        print_utils.print_error(
            f"You gave me more View Layers given than existing! ({view_layer_names})")
      else:
        view_layer_data = []

        for view_layer in view_layer_names:
          view_layer_data.append(current_scene_data.view_layers[view_layer])
    else:
      print_utils.print_error("Unexpected ViewLayer Error.")

    if isinstance(view_layer_data, (bpy.types.bpy_prop_collection, list)):
      for view_layer in view_layer_data:
        view_layer.use = True
    elif isinstance(view_layer_data, bpy.types.ViewLayer):
      view_layer_data.use = True
    else:
      print_utils.print_error("Unexpected ViewLayer Error.")

    # activate add-ons:
    for add_on in add_on_list:
      print_utils.print_info(str(add_on))
      try:
        bpy.ops.preferences.addon_enable(module=add_on)
        print_utils.print_info(f"I activated the addon {add_on}.")
      except AssertionError:
        print_utils.print_error(
            f"I Couldn't find the addon {add_on}. Maybe it's not installed yet?")
    current_scene_render = current_scene_data.render

    try:
      if camera != '':
        current_scene_data.camera = bpy.data.objects[camera]
    except KeyError:
      print_utils.print_error(f"I didn't find the camera called {camera}.")

    # disable render border
    current_scene_render.use_border = border

    if cycles is False:
      if samples != "":
        current_scene_data.eevee.taa_render_samples = int(samples)
      current_scene_render.engine = 'BLENDER_EEVEE'
      current_scene_data.eevee.use_motion_blur = motion_blur
    elif cycles:
      current_scene_render.engine = 'CYCLES'
      if samples != "":
        current_scene_data.cycles.samples = int(samples)

      # cpu
      if render_device == "cpu":
        current_scene_render.threads_mode = 'FIXED'
        current_scene_render.threads = cpu_count() - 2
        current_scene_data.cycles.device = 'CPU'
        try:
          current_scene_render.tile_x = 64
          current_scene_render.tile_y = 64
        except AttributeError:
          print_utils.print_info('You are using the Cycles-x!')

      # gpu
      if render_device == "gpu":
        cycles_pref = bpy.context.preferences.addons['cycles'].preferences
        try:
          cycles_pref.get_devices()
        except ValueError:
          print_utils.print_info(
              "Cycles didn't like me asking about the devices.")
        cycles_pref.compute_device_type = 'OPTIX'

        current_scene_data.cycles.device = 'GPU'

        for cycles_device in cycles_pref.devices:
          if "OPTIX" in str(cycles_device.type):
            cycles_device.use = True
            print_utils.print_info(f"Using device {cycles_device.name}")
          if "CPU" in str(cycles_device.type):
            cycles_device.use = False

          # print_utils.print_info(device.name, device.use)

        try:
          current_scene_render.tile_x = 256
          current_scene_render.tile_y = 256
        except AttributeError:
          print_utils.print_info('You are using the Cycles-x!')

      # motion blur
      current_scene_render.use_motion_blur = motion_blur

      # denoising data
      if isinstance(view_layer_data, (bpy.types.bpy_prop_collection, list)):
        for view_layer in view_layer_data:

          view_layer.cycles.denoising_store_passes = an_denoise
          view_layer.cycles.use_denoising = denoise
      elif isinstance(view_layer_data, bpy.types.ViewLayer):
        view_layer_data.cycles.denoising_store_passes = an_denoise
        view_layer_data.cycles.use_denoising = denoise
      else:
        print_utils.print_error("Denoising handling went wrong.")

      # disable compositing if animation_denoising
      current_scene_render.use_compositing = not an_denoise
      current_scene_data.use_nodes = not an_denoise
      current_scene_data.cycles.use_animated_seed = an_denoise
    current_scene_render.use_compositing = False
    current_scene_data.use_nodes = False
    current_scene_data.cycles.use_animated_seed = True

    print_utils.print_info("Rendering on " + str(render_device))
    # output settings
    if xres != "":
      current_scene_render.resolution_x = int(xres)
    if yres != "":
      current_scene_render.resolution_y = int(yres)
    current_scene_render.resolution_percentage = percres

    # overwrite, placeholder
    current_scene_render.use_overwrite = False
    current_scene_render.use_placeholder = False

    # n-th frame
    current_scene_data.frame_step = frame_step

    print_utils.print_info("Done making the changes in your Blender file.")
  except AssertionError as ass_error:
    print_utils.print_info(ass_error)
    print_utils.write_cache("[ERROR]" + str(ass_error))
    print_utils.print_info("I'm out!")
    time.sleep(2)
    sys.exit()
