from proto import state_pb2

state = state_pb2.render_rob_state()
state.settings.blender_path = "C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe"
state.settings.preview.samples = 10
state.settings.preview.samples_use = True
print(state)
pb_str = state.SerializeToString()
state.ParseFromString(pb_str)
print(vars(state))
print(state)
