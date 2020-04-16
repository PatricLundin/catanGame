
from enum import Enum

class BUILDING_TYPES(Enum):
  VILLAGE = 0
  CITY = 1
  ROAD = 2

class Building:

  # Initializer / Instance Attributes
  def __init__(self, node, player):
    self.type = BUILDING_TYPES.VILLAGE
    self.points = 1
    self.node = node
    self.player = player

  def get_resources(self, type):
    if self.type == BUILDING_TYPES.VILLAGE:
      self.player.cards[type] += 1
    elif self.type == BUILDING_TYPES.CITY:
      self.player.cards[type] += 2

  def upgrade(self):
    if self.type == BUILDING_TYPES.CITY:
      raise Exception("Can't upgrade building that is already a city")
    self.type = BUILDING_TYPES.CITY
    self.points = 2

  def __str__(self):
    return f'type: {self.type}'