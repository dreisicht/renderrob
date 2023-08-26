"""Experiment with the Blender API."""

import unittest

import bpy
from PySide6.QtWidgets import QApplication

from proto import state_pb2


class TestBasic(unittest.TestCase):
  """Test the basic functionality of the Blender API."""

  def test_basic(self):
    """Test the basic functionality of the Blender API."""
    print(bpy.context.scene.name)
    bpy.data.scenes.new("Scene")
    print(bpy.context.scene.name)
    print(state_pb2)
    print(QApplication)
    print("Everything is fine.")
