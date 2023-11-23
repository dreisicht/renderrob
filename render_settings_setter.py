"""This module contains the functions to set the render settings in Blender."""

from typing import List

import bpy  # pylint: disable=import-error

from utils import print_utils, rr_c_image


class RenderSettingsSetter:
  """Class to set the render settings in Blender."""

  def __init__(self, scene: str = None, view_layers: List[str] = None) -> None:
    """Initialize the render settings setter and set the settings."""
    rr_c_image.draw_image()

    print_utils.print_info(
        "Render Rob here. I'm starting to make my changes in your Blender file!")

    self.current_scene_data = None
    self.view_layer_data = None
    self.current_scene_render = None
    if scene and scene not in bpy.data.scenes:
      print_utils.print_warning(
          "I couldn't find the scene you specified. I'm rendering the last used scene.")
    self.set_scene(scene)
    if view_layers != [""]:
      self.set_view_layers(view_layers)

  def set_scene(self, scene_name: str) -> None:
    """Set the scene to be rendered."""
    if not scene_name and len(bpy.data.scenes) > 1:
      print_utils.print_warning(
          "There are more than one scenes, but you didn't tell me which scene to render! So I am"
          " rendering the last used scene.")
      self.current_scene_data = bpy.context.scene
    elif len(bpy.data.scenes) == 1:
      self.current_scene_data = bpy.data.scenes[0]
    else:
      try:
        self.current_scene_data = bpy.data.scenes[scene_name]
      except KeyError:
        print_utils.print_error(f"Scene {scene_name} not found!")
    self.current_scene_render = self.current_scene_data.render

  def set_view_layers(self, view_layer_names: List[str]):
    """Set the view layer to be rendered."""
    for view_layer in self.current_scene_data.view_layers:
      view_layer.use = False

    if isinstance(view_layer_names, str):
      raise ValueError("View Layer names should be a list of strings.")

    if not view_layer_names:
      if len(self.current_scene_data.view_layers) == 1:
        self.view_layer_data = self.current_scene_data.view_layers[0]
      else:
        print_utils.print_info(
            "I'm rendering every active View Layer! You can specify the View Layer to be rendered"
            " in the sheet!")
        self.view_layer_data = self.current_scene_data.view_layers
    elif len(view_layer_names) == 1 and view_layer_names != []:
      if len(self.current_scene_data.view_layers) == 1:
        self.view_layer_data = self.current_scene_data.view_layers[0]
      else:
        try:
          self.view_layer_data = self.current_scene_data.view_layers[view_layer_names[0]]
        except KeyError:
          print_utils.print_error(f"View Layer {view_layer_names[0]} not found. Please check the"
                                  " name in the sheet!")
    elif len(view_layer_names) > 1:
      if len(self.current_scene_data.view_layers) < len(view_layer_names):
        print_utils.print_error(
            f"You gave me more View Layers given than existing! ({view_layer_names})")
      else:
        self.view_layer_data = []

        for view_layer in view_layer_names:
          self.view_layer_data.append(
              self.current_scene_data.view_layers[view_layer])
    else:
      print_utils.print_error("Unexpected ViewLayer Error.")

    if isinstance(self.view_layer_data, (bpy.types.bpy_prop_collection, list)):
      for view_layer in self.view_layer_data:
        view_layer.use = True
    elif isinstance(self.view_layer_data, bpy.types.ViewLayer):
      self.view_layer_data.use = True
    else:
      print_utils.print_error("Unexpected ViewLayer Error.")

  def activate_addons(self, add_on_list: List[str]) -> None:
    """Activate the addons."""
    for addon in add_on_list:
      try:
        bpy.ops.preferences.addon_enable(module=addon)
        print_utils.print_info(f"I activated the addon {addon}.")
      except ModuleNotFoundError:
        print_utils.print_error(
            f"I Couldn't find the addon {addon}. Maybe it's not installed yet?")

  def set_camera(self, camera_name: str,) -> None:
    """Set the camera to be rendered."""
    try:
      if camera_name:
        self.current_scene_data.camera = bpy.data.objects[camera_name]
    except KeyError:
      print_utils.print_error(f"I didn't find the camera called {camera_name}.")

  def set_render_settings(self, render_device: str, border: bool,
                          samples: str, motion_blur: bool, engine: str) -> None:
    """Set the render settings."""
    self.current_scene_render.use_border = border

    if engine.lower() == "eevee":
      if samples:
        self.current_scene_data.eevee.taa_render_samples = int(samples)
      self.current_scene_render.engine = 'BLENDER_EEVEE'
      self.current_scene_data.eevee.use_motion_blur = motion_blur
    elif engine.lower() == "cycles":
      self.current_scene_render.engine = 'CYCLES'
      if samples:
        self.current_scene_data.cycles.samples = int(samples)

      if render_device == "gpu":
        cycles_pref = bpy.context.preferences.addons['cycles'].preferences
        try:
          cycles_pref.get_devices()
        except ValueError:
          print_utils.print_info(
              "Cycles didn't like me asking about the devices.")
        # #1 Add support for multiple GPU types.
        cycles_pref.compute_device_type = 'OPTIX'

        self.current_scene_data.cycles.device = 'GPU'

        for cycles_device in cycles_pref.devices:
          if "OPTIX" in str(cycles_device.type):
            cycles_device.use = True
            print_utils.print_info(f"Using device {cycles_device.name}")
          if "CPU" in str(cycles_device.type):
            cycles_device.use = False

      self.current_scene_render.use_motion_blur = motion_blur

    else:
      raise ValueError(f"Invalid render engine {engine}.")
    print_utils.print_info("Rendering on " + str(render_device))

  def set_denoising_settings(self, denoise: bool) -> None:
    """Set the denoising settings."""
    if denoise:
      self.current_scene_data.cycles.use_animated_seed = True
      bpy.context.scene.cycles.use_denoising = True
    else:
      self.current_scene_data.cycles.use_animated_seed = False
      bpy.context.scene.cycles.use_denoising = False

  def set_output_settings(self, frame_step: int, xres: int,
                          yres: int, percres: int, high_quality: bool, overwrite: bool) -> None:
    """Set the output settings."""
    if xres:
      self.current_scene_render.resolution_x = int(xres)
    if yres:
      self.current_scene_render.resolution_y = int(yres)
    self.current_scene_render.resolution_percentage = percres

    self.current_scene_render.use_overwrite = overwrite
    self.current_scene_render.use_placeholder = False

    self.current_scene_data.frame_step = frame_step
    self.current_scene_data.render.use_stamp = not high_quality
    print_utils.print_info("Finished setting the rendering settings!")

  def custom_commands(self) -> None:
    """Import user commands."""
    try:
      import custom_commands  # pylint: disable=import-error,import-outside-toplevel,unused-import
    except ImportError:
      print_utils.print_info("No user commands found.")
