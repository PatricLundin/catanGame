import uuid
from game.building import BUILDING_TYPES

connectionIdxToNodeIdx = [
  [0, 8],
  [0, 1],
  [2, 1],
  [10, 2],
  [2, 3],
  [4, 3],
  [4, 12],
  [4, 5],
  [6, 5],
  [6, 14],
  [7, 17],
  [7, 8],
  [9, 8],
  [9, 19],
  [10, 9],
  [10, 11],
  [11, 21],
  [12, 11],
  [12, 13],
  [13, 23],
  [13, 14],
  [14, 15],
  [25, 15],
  [27, 16],
  [16, 17],
  [18, 17],
  [29, 18],
  [19, 18],
  [19, 20],
  [20, 31],
  [20, 21],
  [21, 22],
  [33, 22],
  [23, 22],
  [24, 23],
  [24, 35],
  [24, 25],
  [25, 26],
  [37, 26],
  [27, 28],
  [38, 28],
  [29, 28],
  [29, 30],
  [40, 30],
  [30, 31],
  [32, 31],
  [32, 42],
  [32, 33],
  [34, 33],
  [34, 44],
  [35, 34],
  [36, 35],
  [36, 46],
  [36, 37],
  [39, 38],
  [47, 39],
  [39, 40],
  [41, 40],
  [41, 49],
  [41, 42],
  [43, 42],
  [51, 43],
  [43, 44],
  [45, 44],
  [45, 53],
  [45, 46],
  [47, 48],
  [49, 48],
  [49, 50],
  [51, 50],
  [51, 52],
  [52, 53],
]

class Road:

  # Initializer / Instance Attributes
  def __init__(self, nodes, player):
    self.id = str(uuid.uuid4())
    self.type = BUILDING_TYPES.ROAD
    self.nodes = nodes
    self.player = player

  def __str__(self):
    return f'type: {self.type}, pos: {self.nodes[0].x},{self.nodes[0].y} : {self.nodes[1].x},{self.nodes[1].y}'