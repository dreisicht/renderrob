"""Class to store the state of RenderRob."""

import json
from dataclasses import dataclass
from typing import List

from render_job import RenderJob


@dataclass
class RenderRobState:
  """Class to store the state of RenderRob."""

  def __init__(self) -> None:
    """Initialize the state."""
    self.blender_path: str = ""
    self.output_folder: str = ""
    self.blender_files_folder: str = ""
    self.preview_samples: int = 0
    self.preview_nth_frame: int = 0
    self.preview_resolution: int = 100
    self.addons_to_activate: List[str] = []
    self.render_jobs: List[RenderJob] = []

  def open_from_json(self, json_path: str) -> None:
    """Open the state from a JSON file."""
    print(f"Loading state from {json_path}")
    with open(json_path, "r", encoding="UTF-8") as json_file:
      json_dict = json.load(json_file)
      self.blender_path = json_dict["blender_path"]
      self.output_folder = json_dict["output_folder"]
      self.blender_files_folder = json_dict["blender_files_folder"]
      self.preview_samples = json_dict["preview_samples"]
      self.preview_nth_frame = json_dict["preview_nth_frame"]
      self.preview_resolution = json_dict["preview_resolution"]
      self.addons_to_activate = json_dict["addons_to_activate"]
      self.render_jobs = []
      for job_dict in json_dict["render_jobs"]:
        render_job = RenderJob()
        render_job.active = job_dict["active"]
        render_job.file = job_dict["file"]
        render_job.camera = job_dict["camera"]
        render_job.start = job_dict["start"]
        render_job.end = job_dict["end"]
        render_job.x_res = job_dict["x_res"]
        render_job.y_res = job_dict["y_res"]
        render_job.samples = job_dict["samples"]
        render_job.file_format = job_dict["file_format"]
        render_job.engine = job_dict["engine"]
        render_job.device = job_dict["device"]
        render_job.motion_blur = job_dict["motion_blur"]
        render_job.new_version = job_dict["new_version"]
        render_job.high_quality = job_dict["high_quality"]
        render_job.animation_denoise = job_dict["animation_denoise"]
        render_job.denoise = job_dict["denoise"]
        render_job.scene = job_dict["scene"]
        render_job.view_layer = job_dict["view_layer"]
        render_job.comments = job_dict["comments"]
        self.render_jobs.append(render_job)

  def to_dict(self):
    """Convert the state to a dictionary."""
    result = {}
    for key, value in self.__dict__.items():
      if isinstance(value, list):
        result[key] = []
        for item in value:
          result[key].append(item.to_dict())
      else:
        result[key] = value
    return result


if __name__ == "__main__":
  state = RenderRobState()
  state.render_jobs.append(RenderJob())
  # print(state)
  print(state.to_dict())
  # print(RenderJob().to_dict())
  # print(state.__dict__.items())
