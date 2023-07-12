from proto import state_pb2

STATE = state_pb2.render_rob_state()  # pylint: disable=no-member

STATE.settings.blender_path = "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe"
STATE.settings.addons.append("test")
STATE.settings.addons.append("test2")
STATE.settings.output_path = "C:/Users/rober/Desktop"
STATE.settings.blender_files_path = "C:/Users/rober/BlenderFiles"
STATE.settings.preview.samples = 8
STATE.settings.preview.samples_use = False
STATE.settings.preview.frame_step = 5
STATE.settings.preview.frame_step_use = False
STATE.settings.preview.resolution = 50
STATE.settings.preview.resolution_use = False

render_job = state_pb2.render_job()
render_job.active = True
render_job.file = "C:/Users/rober/BlenderFiles/untitled.blend"
render_job.camera = "Camera"
render_job.start = 1
render_job.end = 250
# render_job.x_res = 1920
# render_job.y_res = 1080
render_job.samples = 128
render_job.file_format = state_pb2.file_format.PNG
render_job.render_engine = state_pb2.render_engine.CYCLES
render_job.device = state_pb2.device.GPU
render_job.motion_blur = False
render_job.new_version = False
render_job.high_quality = False
render_job.animation_denoise = False
render_job.denoise = False
render_job.scene = "Scene"
render_job.view_layer = "View Layer"
render_job.comments = "Comments"
STATE.render_jobs.append(render_job)

# pb_str = STATE.SerializeToString()
# new_state = state_pb2.render_rob_state()
# new_state.ParseFromString(pb_str)
