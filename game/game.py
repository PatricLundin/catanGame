from game.board import Board
from game.node import Node, nodeToHex
from game.road import connectionIdxToNodeIdx
from game.player import Player
from game.building import BUILDING_TYPES
import numpy as np
import time

players = [['RED', '0xc94524'], ['BLUE', '0x2469c9'], ['PINK', '0xf092f0'], ['BLACK', '0x242120']]
MAX_TURNS = 1000

class Game:

    # Initializer / Instance Attributes
  def __init__(self, agents):
    self.agents = agents
    self.board = Board.generate_random_board()
    self.players = [Player(self, players[i][0], players[i][1]) for i in range(len(agents))]
    self.nodes = self.init_nodes()
    self.current_turn = 0
    self.num_turns = 0
    self.dice_roll = None
    self.finished = False
    self.time = 0

    for idx, agent in enumerate(agents):
      agent.set_player(self.players[idx])

  def init_nodes(self):
    nodes = [Node(i) for i in range(54)]
    for idx, node in enumerate(nodes):
      boardPositions = nodeToHex[idx]
      for boardIdx in boardPositions:
        self.board[boardIdx].add_node(node)

    for conn in connectionIdxToNodeIdx:
      nodes[conn[0]].add_connection(nodes[conn[1]])
      nodes[conn[1]].add_connection(nodes[conn[0]])
    return nodes

  def turn(self):
    self.num_turns += 1
    self.current_turn = (self.current_turn + 1) % len(self.players)
    self.dice_roll = self.roll_dice()
    self.distribute_cards()
    # print('Turns:', self.num_turns, 'Points:', [a.player.get_points() for a in self.agents], 'Actions:', len(self.agents[self.current_turn].player.get_actions()), 'Cards:', self.agents[self.current_turn].player.cards_to_string())
    self.agents[self.current_turn].turn()
    if self.check_winner():
      self.finished = True
      for agent in self.agents:
        agent.clear_player()

  def roll_dice(self):
    dice1 = np.random.randint(1, 7)
    dice2 = np.random.randint(1, 7)
    return [dice1, dice2, dice1 + dice2]

  def distribute_cards(self):
    for tile in self.board:
      if tile.value == self.dice_roll[2]:
        tile.distribute_cards()

  def check_winner(self):
    return self.agents[self.current_turn].player.get_points() >= 10

  def choose_starting_villages(self):
    for agent in self.agents:
      agent.choose_starting_village()
    for agent in reversed(self.agents):
      agent.choose_starting_village()

  def run_game(self, player):
    start_time = time.time()
    self.choose_starting_villages()

    while (not self.finished and self.num_turns < MAX_TURNS):
      self.turn()
    self.time = time.time() - start_time

  def get_state(self, player):
    # Board types:
    board_types = [y for x in [Board.type_to_input_arr(tile.type) for tile in self.board] for y in x]
    # Board values:
    board_values = Board.values_to_input_arr([0 if tile.value is None else tile.value for tile in self.board])

    # Buildings on nodes
    buildings = []
    for node in self.nodes:
      if not node.building:
        buildings.append(0)
      else:
        player_building = node.building.player.id == player.id
        building_type = 0.5 if node.building.type == BUILDING_TYPES.VILLAGE else 1
        buildings.append(0 + building_type if player_building else 0 - building_type)
    
    # Roads on connections
    roads = []
    for conn in connectionIdxToNodeIdx:
      nodes = [self.nodes[conn[0]], self.nodes[conn[1]]]
      if all(len(node.roads) == 0 for node in nodes):
        roads.append(0)
        continue
      found = False
      for r1 in nodes[0].roads:
        for r2 in nodes[1].roads:
          if r1.id == r2.id:
            found = True
            if r1.player.id == player.id:
              roads.append(1)
            else:
              roads.append(-1)
      if not found:
        roads.append(0)

    return board_types + board_values + buildings + roads