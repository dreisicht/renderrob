"""Class to store the local state of RenderRob."""

from typing import List


class localState:
  """Class to store the local state of RenderRob."""

  def __init__(self) -> None:
    """Initialize the state."""
    self.current_file: str = ""
    self.last_files: List[str] = []

  # def to_dict(self):
  #   """Return the state as a dictionary."""
  #   return {"current_file": self.current_file, "last_files": self.last_files}
