from enum import Enum
from game.tile import Tile
from game.node import harbor_nodes
from game.enums import GRID_TYPES, HARBOR_TYPES
import numpy as np

all_values = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

def gaussianNormalization(values):
  mean = np.sum(values) / len(values)
  variance = np.sum([(v - mean) ** 2 for v in values]) / len(values)
  std_dev = np.sqrt(variance)
  return [(v - mean) / std_dev for v in values]

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

  @staticmethod
  def add_harbors_to_nodes(nodes):
    available_harbors = {
      HARBOR_TYPES.THREE_TO_ONE: 4,
      HARBOR_TYPES.WHEAT: 1,
      HARBOR_TYPES.WOOD: 1,
      HARBOR_TYPES.SHEEP: 1,
      HARBOR_TYPES.STONE: 1,
      HARBOR_TYPES.BRICKS: 1,
    } 
    b = list(map(lambda item: [item[0]] * item[1], available_harbors.items()))
    harbors = [item for sublist in b for item in sublist]
    np.random.shuffle(harbors)
    possible_nodes = [nodes[idx] for idx in harbor_nodes]
    gaps = [2, 1, 1, 2, 1, 1, 2, 1, 1]
    np.random.shuffle(gaps)
    start_idx = np.random.choice(np.arange(len(possible_nodes)))

    for harbor in harbors:
      possible_nodes[start_idx].set_harbor(harbor)
      possible_nodes[(start_idx + 1) % len(possible_nodes)].set_harbor(harbor)
      start_idx = (start_idx + 2 + gaps.pop()) % len(possible_nodes)


  @staticmethod
  def type_to_input_arr(type):
    # grid_arr = [0] * 6
    # grid_arr[type.value] = 1
    # return grid_arr
    return type.value

  @staticmethod
  def values_to_input_arr(values):
    points = {
      0: 0,
      2: 1,
      3: 2,
      4: 3,
      5: 4,
      6: 5,
      8: 5,
      9: 4,
      10: 3,
      11: 2,
      12: 1
    }
    return [points[v] for v in values]