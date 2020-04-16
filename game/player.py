import uuid
from enum import Enum
from game.building import Building, BUILDING_TYPES
from game.board import GRID_TYPES
from game.road import Road

def building_costs(building):
  if building == BUILDING_TYPES.VILLAGE:
    return {
      GRID_TYPES.SHEEP: 1,
      GRID_TYPES.WHEAT: 1,
      GRID_TYPES.WOOD: 1,
      GRID_TYPES.BRICKS: 1,
    }
  elif building == BUILDING_TYPES.CITY:
    return {
      GRID_TYPES.WHEAT: 2,
      GRID_TYPES.STONE: 3,
    }
  elif building == BUILDING_TYPES.ROAD:
    return {
      GRID_TYPES.BRICKS: 1,
      GRID_TYPES.WOOD: 1,
    }
  raise Exception('Type need to be a BUILDING_TYPES type')

class Player:

  # Initializer / Instance Attributes
  def __init__(self, game, name, color):
    self.id = str(uuid.uuid4())
    self.game = game
    self.name = name
    self.color = color
    self.buildings = []
    self.roads = []
    self.cards = {
      GRID_TYPES.WHEAT: 2,
      GRID_TYPES.STONE: 0,
      GRID_TYPES.BRICKS: 4,
      GRID_TYPES.WOOD: 4,
      GRID_TYPES.SHEEP: 2,
    }

  def can_build(self, type):
    for costs in building_costs(type).items():
      if self.cards[costs[0]] < costs[1]:
        return False
    return True

  def buildRoad(self, nodes):
    road = Road(nodes, self)
    self.roads.append(road)
    for node in nodes:
      node.add_road(road)
    for costs in building_costs(BUILDING_TYPES.ROAD).items():
      self.cards[costs[0]] -= costs[1]

  def build_building(self, node):
    if node.building:
      raise Exception("Can't build building on a node with a building")
    building = Building(node, self)
    self.buildings.append(building)
    node.set_building(building)
    for costs in building_costs(BUILDING_TYPES.VILLAGE).items():
      self.cards[costs[0]] -= costs[1]

  def upgrade_building(self, building):
    building.upgrade()
    for costs in building_costs(BUILDING_TYPES.CITY).items():
      self.cards[costs[0]] -= costs[1]

  def __str__(self):
    return f'name: {self.name}, color: {self.color}, id: {self.id}'