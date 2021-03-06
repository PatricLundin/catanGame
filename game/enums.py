from enum import Enum

class GRID_TYPES(int, Enum):
  DESERT = 0
  STONE = 1
  WOOD = 2
  WHEAT = 3
  BRICKS = 4
  SHEEP = 5

class HARBOR_TYPES(Enum):
  THREE_TO_ONE = 0
  WHEAT = GRID_TYPES.WHEAT
  BRICKS = GRID_TYPES.BRICKS
  WOOD = GRID_TYPES.WOOD
  STONE = GRID_TYPES.STONE
  SHEEP = GRID_TYPES.SHEEP

class STRATEGIES(str, Enum):
  RANDOM = 'RANDOM'
  ALLACTIONS = 'ALLACTIONS'
  EVALUATE = 'EVALUATE'

class BUILDING_TYPES(Enum):
  VILLAGE = 0
  CITY = 1
  ROAD = 2

class Actions(str, Enum):
  NOACTION = 'noAction'
  BUILDING = 'building'
  UPGRADE = 'upgrade'
  ROAD = 'road'
  TRADE = 'trade'