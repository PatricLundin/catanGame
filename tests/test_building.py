import unittest
from game.building import Building, BUILDING_TYPES
from game.board import GRID_TYPES
from game.node import Node
import numpy as np

class TestBuildingClass(unittest.TestCase):

  def test_create_building(self):
    player = {
      'cards': {
        GRID_TYPES.WHEAT: 0,
        GRID_TYPES.STONE: 0,
        GRID_TYPES.BRICKS: 0,
        GRID_TYPES.WOOD: 0,
        GRID_TYPES.SHEEP: 0,
      }
    }
    building = Building({}, player)
    self.assertIsNotNone(building)
