"""Experiment with the Blender API."""

import bpy

print(bpy.context.scene.name)
bpy.data.scenes.new("Scene")
print(bpy.context.scene.name)
