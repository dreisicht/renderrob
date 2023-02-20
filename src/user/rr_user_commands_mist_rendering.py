# Place your custom python commands here. They get exectued in very job before rendering a frame.
import bpy


def bake_particles():
  for scene in bpy.data.scenes:
    for object in scene.objects:
      for modifier in object.modifiers:
        if modifier.type == 'PARTICLE_SYSTEM':
          print("Baking particles")
          override = {'scene': scene, 'active_object': object, 'point_cache': modifier.particle_system.point_cache}
          bpy.ops.ptcache.free_bake(override)
          bpy.ops.ptcache.bake(override, bake=True)


bake_particles()
bpy.context.scene.view_layers["main"].use_pass_cryptomatte_material = False
# bpy.context.scene.view_layers["env"].use = True
bpy.context.scene.cycles.use_denoising = False


for i in range(len(bpy.context.scene.view_layers['main'].aovs)):
  bpy.ops.scene.view_layer_remove_aov()
bpy.context.scene.view_layers["main"].use_pass_mist = True
bpy.context.scene.view_layers["main"].use_pass_normal = False
bpy.context.scene.view_layers["main"].use_pass_z = False
bpy.context.scene.view_layers["main"].cycles.denoising_store_passes = False

# bpy.context.scene.view_layers["env"].use_pass_normal = False
# bpy.context.scene.view_layers["env"].use_pass_z = False
# bpy.context.scene.view_layers["env"].cycles.denoising_store_passes = False


bpy.context.scene.cycles.aa_samples = 8
# bpy.data.scenes["Scene"].cycles.denoiser = 'NLM'
bpy.context.scene.render.image_settings.use_preview = True


bpy.data.objects["porsche_turbo_x.001_proxy"].pose.bones["spoiler_root"].constraints["Limit Location"].max_y = 0.1
bpy.data.objects['smoke_domain'].hide_render = True
