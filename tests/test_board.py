import unittest
from game.board import Board, GRID_TYPES
from game.tile import Tile
import numpy as np

class TestBoardClass(unittest.TestCase):

  def test_type_to_input_arr(self):
    for type in GRID_TYPES:
      input_arr = Board.type_to_input_arr(type)
      self.assertEqual(np.sum(input_arr), 1)
      self.assertEqual(input_arr[type.value], 1)

  def test_values_to_input_arr(self):
    values = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
    input_arr = Board.values_to_input_arr(values)
    for val in input_arr:
      self.assertTrue(val > -2 and val < 2)

  def test_generate_random_board(self):
    board = Board.generate_random_board()
    self.assertEqual(len(board), 19)
    truth_num = {
      GRID_TYPES.DESERT: 1,
      GRID_TYPES.STONE: 3,
      GRID_TYPES.BRICKS: 3,
      GRID_TYPES.SHEEP: 4,
      GRID_TYPES.WHEAT: 4,
      GRID_TYPES.WOOD: 4,
    }
    counts = {
      GRID_TYPES.DESERT: 0,
      GRID_TYPES.STONE: 0,
      GRID_TYPES.BRICKS: 0,
      GRID_TYPES.SHEEP: 0,
      GRID_TYPES.WHEAT: 0,
      GRID_TYPES.WOOD: 0,
    }
    for tile in board:
      self.assertIsInstance(tile, Tile)
      self.assertIsInstance(tile.type, GRID_TYPES)
      if tile.type == GRID_TYPES.DESERT:
        self.assertIsNone(tile.value)
      else:
        self.assertIsInstance(tile.value, int)
      counts[tile.type] += 1

    for t in truth_num:
      self.assertEqual(counts[t], truth_num[t])
