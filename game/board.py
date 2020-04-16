from enum import Enum
from game.tile import Tile
import numpy as np

class GRID_TYPES(Enum):
  DESERT = 0
  STONE = 1
  WOOD = 2
  WHEAT = 3
  BRICKS = 4
  SHEEP = 5

class Board:
  
  @staticmethod
  def generate_random_board():
    available_types = {
      GRID_TYPES.STONE: 3,
      GRID_TYPES.WOOD: 4,
      GRID_TYPES.WHEAT: 4,
      GRID_TYPES.BRICKS: 3,
      GRID_TYPES.SHEEP: 4,
    }

    b = list(map(lambda item: [item[0]] * item[1], available_types.items()))
    types = [item for sublist in b for item in sublist]
    np.random.shuffle(types)
    values = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
    np.random.shuffle(values)

    tileData = [[types[i], values[i]] for i in range(len(types))]
    tileData.append([GRID_TYPES.DESERT, None])
    np.random.shuffle(tileData)
    return [Tile(i, d[0], d[1]) for i, d in enumerate(tileData)]
