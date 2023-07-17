"""Tests for renderscript.py."""

import unittest
from unittest.mock import patch

import bpy

import renderscript


class TestRenderSettingsSetter(unittest.TestCase):
  """Tests for the RenderSettingsSetter class."""

  def setUp(self):
    self.rss = renderscript.RenderSettingsSetter()

  def test_set_scene(self):
    bpy.data.scenes[0].name = "scene_a"
    self.rss.set_scene("scene_a")
    self.assertEqual(bpy.context.scene.name, "scene_a")

  def test_set_scene_single_scene(self):
    bpy.data.scenes.new("Scene")
    self.rss.set_scene("Scene")
    self.assertEqual(self.rss.current_scene_data.name, "Scene")

  def test_set_scene_multiple_scenes_with_scene_name(self):
    bpy.data.scenes.new("Scene1")
    bpy.data.scenes.new("Scene2")
    self.rss.set_scene("Scene2")
    self.assertEqual(self.rss.current_scene_data.name, "Scene2")

  def test_set_scene_multiple_scenes_without_scene_name(self):
    bpy.data.scenes.new("Scene1")
    bpy.data.scenes.new("Scene2")
    with patch("builtins.print"):
      self.rss.set_scene("Scene2")
    self.rss.current_scene_data.name
    self.assertEqual(self.rss.current_scene_data.name, "Scene2")

  def test_set_scene_nonexistent_scene_name(self):
    new_scene = bpy.data.scenes.new("SceneAF")
    bpy.context.window.scene = new_scene

    with patch("utils.print_utils.print_error") as mock_print_error:
      self.rss.set_scene("NonexistentScene")
    mock_print_error.assert_called_with(
        f"Scene NonexistentScene not found!")
    self.assertEqual(new_scene.name, "SceneAF")

  def test_set_view_layer_single_view_layer(self):
    scene = bpy.context.scene
    bpy.context.window.view_layer = scene.view_layers.new("View Layer")
    self.rss.set_view_layers(["View Layer"])
    self.assertTrue(self.rss.view_layer_data.use)

  def test_set_view_layer_multiple_view_layers(self):
    scene = bpy.context.scene
    scene.view_layers.new("View Layer1")
    scene.view_layers.new("View Layer2")
    self.rss.set_view_layers(["View Layer1", "View Layer2"])
    self.assertEqual(len(self.rss.view_layer_data), 2)
    for view_layer in self.rss.view_layer_data:
      self.assertTrue(view_layer.use)

  def test_set_view_layer_empty_view_layer_list(self):
    scene = bpy.context.scene
    bpy.context.window.view_layer = scene.view_layers.new("View Layer")
    with patch("builtins.print"):
      self.rss.set_view_layers([])
    self.assertEqual(len(self.rss.view_layer_data), 2)
    self.assertTrue(bpy.context.window.view_layer.use)

  def test_set_view_layer_nonexistent_view_layer(self):
    scene = bpy.context.scene
    bpy.context.window.view_layer = scene.view_layers.new("View Layer")
    with patch("utils.print_utils.print_error") as mock_print_error:
      self.rss.set_view_layers(["NonexistentViewLayer"])
    mock_print_error.assert_called_with(
        f"View Layer NonexistentViewLayer not found. Please check the name in the sheet!")

  def test_activate_addons(self):
    addon_name = "mesh_f2"
    bpy.ops.preferences.addon_enable = mock_enable_addon
    with patch("utils.print_utils.print_info") as mock_print_info:
      self.rss.activate_addons([addon_name])

  def test_set_camera_existing_camera(self):
    bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.scene.camera = bpy.data.objects["Camera"]
    self.rss.set_camera("Camera")
    self.assertEqual(self.rss.current_scene_data.camera.name, "Camera")

  def test_set_camera_nonexistent_camera(self):
    bpy.data.objects.new("Camera2", bpy.data.cameras.new("Camera2"))
    with patch("utils.print_utils.print_error") as mock_print_error:
      self.rss.set_camera("NonexistentCamera")
    mock_print_error.assert_called_with(
        "I didn't find the camera called NonexistentCamera.")

  def test_set_render_settings_cpu_engine(self):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_motion_blur = True
    self.rss.set_render_settings("cpu", False, 128, False, "EEVEE")
    self.assertEqual(scene.render.engine, "BLENDER_EEVEE")
    self.assertEqual(scene.cycles.samples, 128)
    self.assertEqual(scene.cycles.device, "CPU")
    self.assertFalse(scene.eevee.use_motion_blur)

  def test_set_render_settings_gpu_engine(self):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_motion_blur = True
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "OPTIX"
    self.rss.set_render_settings("gpu", False, 128, False, "CYCLES")
    self.assertEqual(scene.render.engine, "CYCLES")
    self.assertEqual(scene.cycles.samples, 128)
    self.assertEqual(scene.cycles.device, "GPU")
    self.assertTrue(any(
        device.use for device in bpy.context.preferences.addons["cycles"].preferences.devices if "OPTIX" in str(device.type)))
    self.assertFalse(any(
        device.use for device in bpy.context.preferences.addons["cycles"].preferences.devices if "CPU" in str(device.type)))
    self.assertFalse(scene.render.use_motion_blur)

  def test_set_denoising_settings_multiple_view_layers(self):
    scene = bpy.context.scene
    scene.view_layers.new("View Layer1")
    scene.view_layers.new("View Layer2")
    self.rss.current_scene_data = scene
    self.rss.view_layer_data = [
        scene.view_layers["View Layer1"], scene.view_layers["View Layer2"]]
    self.rss.set_denoising_settings(False, False)
    for view_layer in self.rss.view_layer_data:
      self.assertEqual(view_layer.cycles.denoising_store_passes, False)
      self.assertEqual(view_layer.cycles.use_denoising, False)
    self.assertEqual(self.rss.current_scene_render.use_compositing, False)
    self.assertEqual(self.rss.current_scene_data.use_nodes, False)
    self.assertEqual(self.rss.current_scene_data.cycles.use_animated_seed, True)

  def test_set_output_settings(self):
    scene = bpy.context.scene
    scene.render.resolution_x = 100
    scene.render.resolution_y = 100
    scene.render.resolution_percentage = 100
    scene.frame_step = 1
    rss = renderscript.RenderSettingsSetter()
    rss.set_output_settings(128, 2, 1920, 1080, 50)
    self.assertEqual(scene.render.resolution_x, 1920)
    self.assertEqual(scene.render.resolution_y, 1080)
    self.assertEqual(scene.render.resolution_percentage, 50)
    self.assertEqual(scene.frame_step, 2)


if __name__ == "__main__":
  unittest.main()
