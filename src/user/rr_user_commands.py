# Place your custom python commands here. They get exectued in very job before rendering a frame.
import bpy

# FOR FINAL RENDER


def main():
  bpy.context.scene.render.use_border = False
  bpy.context.scene.render.film_transparent = False
