"""Setup for cx_freeze."""

import sys
from cx_Freeze import setup, Executable


def main():
  """Setup for cx_freeze."""
  # Dependencies are automatically detected, but it might need fine tuning.
  build_exe_options = {
      "excludes": ["tkinter", "unittest"],
      "zip_include_packages": ["encodings", "PySide6", "protos"],
  }

  # base="Win32GUI" should be used only for Windows GUI app
  base = "Win32GUI" if sys.platform == "win32" else None

  icon = "icons/icon.ico"
  setup(
      name="renderrob",
      version="0.1",
      description="RenderRob",
      options={"build_exe": build_exe_options},
      executables=[Executable("renderrob.py", base=base, icon=icon)],
  )


main()
