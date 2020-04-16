import uuid
from enum import Enum
from game.building import Building, BUILDING_TYPES
from game.board import GRID_TYPES
from game.road import Road, connectionIdxToNodeIdx

class Actions(Enum):
  NOACTION = 0
  BUILDING = 1
  UPGRADE = 2
  ROAD = 3
  TRADE = 4

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
    self.actions = []

  def cards_to_string(self):
    return f'Wh: {self.cards[GRID_TYPES.WHEAT]}, St: {self.cards[GRID_TYPES.STONE]}, B: {self.cards[GRID_TYPES.BRICKS]}, Wo: {self.cards[GRID_TYPES.WOOD]}, Sh: {self.cards[GRID_TYPES.SHEEP]}'

  def can_build(self, type):
    for costs in building_costs(type).items():
      if self.cards[costs[0]] < costs[1]:
        return False
    return True

  def can_trade(self, type):
    return self.cards[type] >= 4

  def buildRoad(self, nodes):
    # print('ROAD on ', nodes[0], nodes[1])
    road = Road(nodes, self)
    self.roads.append(road)
    for node in nodes:
      node.add_road(road)
    for costs in building_costs(BUILDING_TYPES.ROAD).items():
      self.cards[costs[0]] -= costs[1]

  def build_building(self, node):
    # print('BUILDING on ', node)
    if node.building:
      raise Exception("Can't build building on a node with a building")
    building = Building(node, self)
    self.buildings.append(building)
    node.set_building(building)
    for costs in building_costs(BUILDING_TYPES.VILLAGE).items():
      self.cards[costs[0]] -= costs[1]

  def upgrade_building(self, building):
    # print('UPGRADE on ', building.node)
    building.upgrade()
    for costs in building_costs(BUILDING_TYPES.CITY).items():
      self.cards[costs[0]] -= costs[1]

  def make_trade(self, fr, to):
    # print('TRADE from', fr, 'to', to)
    self.cards[fr] -= 4
    self.cards[to] += 1

  def can_build_village_on_node(self, node):
    return (
      self.can_build(BUILDING_TYPES.VILLAGE)
      and not node.building
      and not any(n.building is not None for n in node.connections)
      and any(any(n.id == node.id for n in r.nodes) for r in self.roads)
    )

  def can_build_city_on_node(self, node):
    return (
      self.can_build(BUILDING_TYPES.CITY)
      and any((b.node.id == node.id and b.type == BUILDING_TYPES.VILLAGE) for b in self.buildings)
    )

  def can_build_road_on_conn(self, nodes):
    return (
      self.can_build(BUILDING_TYPES.ROAD)
      and not any(any(r.id == road.id for r in nodes[1].roads) for road in nodes[0].roads)
      and any(any((nodes[0].id == n.id or nodes[1].id == n.id) for n in road.nodes) for road in self.roads)
    )

  def get_starting_building_actions(self):
    do_nothing = [None]
    v_pred = lambda n: (n.building is None and all(n1.building is None for n1 in n.connections))
    villages = [[Actions.BUILDING, idx] if v_pred(node) else None for idx, node in enumerate(self.game.nodes)]
    cities = [None] * len(self.game.nodes)
    roads = [None] * len(connectionIdxToNodeIdx)
    trades = [None] * 20
    return do_nothing + villages + cities + roads + trades

  def get_starting_road_actions(self, node):
    do_nothing = [None]
    villages = [None] * len(self.game.nodes)
    cities = [None] * len(self.game.nodes)
    r_pred = lambda c: any(self.game.nodes[nIdx].id == node.id for nIdx in c)
    roads = [[Actions.ROAD, idx] if r_pred(conn) else None for idx, conn in enumerate(connectionIdxToNodeIdx)]
    trades = [None] * 20
    return do_nothing + villages + cities + roads + trades

  def get_all_actions(self):
    do_nothing = [[Actions.NOACTION, 0]]
    villages = [[Actions.BUILDING, idx] if self.can_build_village_on_node(node) else None for idx, node in enumerate(self.game.nodes)]
    cities = [[Actions.UPGRADE, idx] if self.can_build_city_on_node(node) else None for idx, node in enumerate(self.game.nodes)]
    roads = [[Actions.ROAD, idx] if self.can_build_road_on_conn([self.game.nodes[n] for n in conn]) else None for idx, conn in enumerate(connectionIdxToNodeIdx)]
    trades = []
    for r1 in self.cards.keys():
      for r2 in self.cards.keys():
        if not r1 == r2 and self.can_trade(r1):
          trades.append([Actions.TRADE, r1, r2])
        else:
          trades.append(None)
    return do_nothing + villages + cities + roads + trades

  def get_actions(self):
    return list(filter(lambda a: a is not None, self.get_all_actions()))

  def take_action(self, action):
    self.actions.append(action)
    type = action[0]
    idx = action[1]
    if type == Actions.BUILDING:
      self.build_building(self.game.nodes[idx])
    elif type == Actions.UPGRADE:
      self.upgrade_building(self.game.nodes[idx].building)
    elif type == Actions.ROAD:
      self.buildRoad([self.game.nodes[n] for n in connectionIdxToNodeIdx[idx]])
    elif type == Actions.TRADE:
      self.make_trade(action[1], action[2])

  def get_points(self):
    sum = 0
    for building in self.buildings:
      sum += building.points
    return sum

  def __str__(self):
    return f'name: {self.name}, color: {self.color}, id: {self.id}'