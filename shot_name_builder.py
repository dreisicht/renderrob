"""Class to build a shot name from the render job."""

import os
import pathlib

from protos import state_pb2
from utils_rr import ui_utils


def still_or_animation(start: str, end: str) -> str:
  """Return 'still' or 'animation' depending on the render job."""
  if start == "" and end == "":
    return "ANIMATION"
  if start != "" and end != "":
    return "ANIMATION"
  if start != "" and end == "":
    return "STILL"
  if start == "" and end != "":
    raise ValueError("End frame is set, but start frame is not.")
  raise ValueError("Could not determine of still or animation.")


class ShotNameBuilder:
  """Class to build a shot name from the render job."""

  def __init__(self, render_job: state_pb2.render_job,  # pylint: disable=no-member
               output_path: str, is_replay_mode: bool = False) -> None:
    """Initialize the shot name builder.

    Args:
      render_job: The render job to build the shot name from.
      output_path: The path to the output folder.
      is_replay_mode: Whether the path is used for showing the result. If so, the version number
        is not increased.
    """
    self.render_job = render_job
    self.replay_mode = is_replay_mode
    self.shotname = self.get_shotname()
    self.frame_path = self.get_full_frame_path(output_path, self.shotname)

  def get_shotname(self) -> str:
    """Build the shot name from the render job."""
    if self.render_job.high_quality:
      quality_state_string = "hq"
    else:
      quality_state_string = "pv"

    if isinstance(self.render_job.view_layers, str):
      raise ValueError("View layer is not a list.")

    # The default view layer does not need to be in the shot name.
    if self.render_job.view_layers == ["View Layer"]:
      view_layer_name = None
    else:
      view_layer_name = "+".join(
          self.render_job.view_layers).lower().replace("view layer", "Vl")

    # The default camera does not need to be in the shot name.
    if self.render_job.camera.lower() == "camera":
      camera_name = None
    else:
      camera_name = self.render_job.camera.lower().replace("camera", "Cam")

    # The default scene does not need to be in the shot name.
    if self.render_job.scene.lower() == "scene":
      scene_name = None
    else:
      scene_name = self.render_job.scene.lower().replace("scene", "Sc")

    blend_filename = os.path.basename(
        self.render_job.file).replace(".blend", "")
    shotname_arr = [blend_filename, camera_name, scene_name, view_layer_name,
                    quality_state_string, "v$$"]

    return "-".join(filter(None, shotname_arr)).replace(" ", "_")

  def set_version_number(self, full_frame_path: str) -> str:
    """Get the version number of the shot."""
    _full_frame_path = pathlib.Path(full_frame_path)
    for shot_iter_num in range(1000, -1, -1):
      # STILL
      if "v$$" not in _full_frame_path.parent.parts[-1]:
        still_path = full_frame_path.replace("v$$", "v" + str(shot_iter_num).zfill(2))
        if pathlib.Path(still_path).exists():
          break
        continue
      # ANIMATION
      folderpath_str = str(_full_frame_path.parent).replace(
          "v$$", "v" + str(shot_iter_num).zfill(2))
      folderpath = pathlib.Path(folderpath_str)
      if folderpath.exists():
        if any(folderpath.iterdir()):
          break
        shot_iter_num -= 1
        break

    shot_iter_num += 1
    if shot_iter_num > 1:
      if self.replay_mode:
        shot_iter_num -= 1
      elif self.render_job.overwrite:
        shot_iter_num -= 1

    # Update full_frame_path with iteration number.
    return full_frame_path.replace(
        "v$$", f"v{str(shot_iter_num).zfill(2)}")

  def get_full_frame_path(self, output_path: str, shotname: str) -> str:
    """Build the path to the frames including the file name and directory."""
    if not output_path:
      output_path = str(pathlib.Path(self.render_job.file).parent)
    output_path = output_path.replace("\\", "/")

    frame_name = f"{shotname}-f####.{ui_utils.FILE_FORMATS_ACTUAL[self.render_job.file_format]}"
    if "STILL" == still_or_animation(self.render_job.start, self.render_job.end):
      frame_render_folder = os.path.join(output_path, "stills")
      frame_name = frame_name.replace("f####", f"f{str(self.render_job.start).zfill(4)}")
    else:
      frame_render_folder = os.path.join(output_path, shotname)

    full_frame_path = os.path.join(frame_render_folder, frame_name)
    full_frame_path = self.set_version_number(full_frame_path)

    if "STILL" == still_or_animation(self.render_job.start, self.render_job.end):
      full_frame_path = full_frame_path.replace(f"f{str(self.render_job.start).zfill(4)}", "f####")

    return full_frame_path.replace("\\", "/")
