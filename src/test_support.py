"""Helpers that keep the unit tests away from the files a real Render Rob session uses.

On Linux the cache lives in the working directory, which for both `just test` and `just run` is
src/. A test that opens a fixture would otherwise leave that fixture in the app's Open Recent list
and as its current file, so the next Ctrl+S in the app would overwrite the tracked fixture.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import main

FIXTURE_DIR = Path(__file__).parent.parent / "test"


def make_temp_dir(test_case: unittest.TestCase) -> Path:
  """Create a directory that is removed again once the test is over."""
  temp_dir = tempfile.TemporaryDirectory()
  test_case.addCleanup(temp_dir.cleanup)
  return Path(temp_dir.name)


def make_main_window(test_case: unittest.TestCase) -> main.MainWindow:
  """Build and set up a main window whose cache lives in a throwaway directory."""
  main_window = main.MainWindow()  # pylint:disable=no-member
  main_window.cache_path = make_temp_dir(test_case) / ".rr_cache"
  main_window.setup()
  return main_window


def copy_fixture(test_case: unittest.TestCase, file_name: str) -> str:
  """Copy a fixture into a throwaway directory, so a test that saves cannot change the original."""
  destination = make_temp_dir(test_case) / file_name
  shutil.copyfile(FIXTURE_DIR / file_name, destination)
  return str(destination)
