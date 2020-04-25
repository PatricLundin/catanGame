from game.board import Board
from game.node import Node, nodeToHex, harbor_nodes
from game.road import connectionIdxToNodeIdx
from game.player import Player
from game.agent import Agent
from game.enums import BUILDING_TYPES, STRATEGIES, HARBOR_TYPES
from game.turn import Turn
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
    self.winner = None
    self.time = 0
    self.turn_data = []

  def init_nodes(self):
    nodes = [Node(i) for i in range(54)]
    for idx, node in enumerate(nodes):
      boardPositions = nodeToHex[idx]
      for boardIdx in boardPositions:
        self.board[boardIdx].add_node(node)

    for conn in connectionIdxToNodeIdx:
      nodes[conn[0]].add_connection(nodes[conn[1]])
      nodes[conn[1]].add_connection(nodes[conn[0]])
    Board.add_harbors_to_nodes(nodes)
    return nodes

  def turn(self):
    self.num_turns += 1
    self.current_turn = (self.current_turn + 1) % len(self.players)
    self.dice_roll = self.roll_dice()
    self.distribute_cards()
    # print('Turns:', self.num_turns, 'Points:', [a.player.get_points() for a in self.agents], 'Actions:', len(self.agents[self.current_turn].player.get_actions()), 'Cards:', self.agents[self.current_turn].player.cards_to_string())
    playerTurn = self.agents[self.current_turn].turn(self.players[self.current_turn], self.num_turns)
    self.turn_data.append(Turn(self.num_turns, self.players[self.current_turn], playerTurn, self.dice_roll))
    if self.check_winner():
      self.finished = True

  def roll_dice(self):
    dice1 = np.random.randint(1, 7)
    dice2 = np.random.randint(1, 7)
    return [dice1, dice2, dice1 + dice2]

  def distribute_cards(self):
    for tile in self.board:
      if tile.value == self.dice_roll[2]:
        tile.distribute_cards()

  def check_winner(self):
    return self.players[self.current_turn].get_points() >= 10

  def choose_starting_villages(self):
    for idx, agent in enumerate(self.agents):
      agent.choose_starting_village(self.players[idx])
    for idx, agent in reversed(list(enumerate(self.agents))):
      agent.choose_starting_village(self.players[idx])

  def run_game(self):
    start_time = time.time()
    self.choose_starting_villages()

    while (not self.finished and self.num_turns < MAX_TURNS):
      self.turn()
    self.time = time.time() - start_time
    if (self.finished):
      self.winner = self.agents[self.current_turn].id
    else:
      self.winner = self.agents[np.argmax([player.get_points() for player in self.players])].id
    print('Game finished')

  def run_num_turns_and_finish(self, n):
    max_turns = self.num_turns + n
    while (not self.finished and self.num_turns < max_turns):
      self.turn()
    if (self.finished):
      self.winner = self.agents[self.current_turn].id
    else:
      self.winner = self.agents[np.argmax([player.get_points() for player in self.players])].id

  def run_rest_of_game(self):
    while (not self.finished and self.num_turns < MAX_TURNS):
      self.turn()
    if (self.finished):
      self.winner = self.agents[self.current_turn].id
    else:
      self.winner = self.agents[np.argmax([player.get_points() for player in self.players])].id

  def simulateAction(self, action):
    game = Game(self.agents)
    game.current_turn = self.current_turn
    for idx, tile in enumerate(game.board):
      tile.set_state(self.board[idx].get_state())
    for idx, player in enumerate(game.players):
      player.set_state(self.players[idx].get_state())
    game.players[game.current_turn].take_action(action)
    # TODO: play until your turn again
    return game.get_state(game.players[game.current_turn])

  def simulateGame(self, action):
    agents = []
    for agent in self.agents:
      a = Agent(STRATEGIES.RANDOM, agent.layers)
      a.id = agent.id
      agents.append(a)
    game = Game(agents)
    game.current_turn = self.current_turn
    game.num_turns = self.num_turns
    for idx, tile in enumerate(game.board):
      tile.set_state(self.board[idx].get_state())
    for idx, player in enumerate(game.players):
      player.set_state(self.players[idx].get_state())
    game.players[game.current_turn].take_action(action)
    game.run_num_turns_and_finish(100)
    return game.winner

  def get_villages(self):
    num_villages = 0
    for node in self.nodes:
      if node.building:
        num_villages +=1
    return num_villages

  def get_cities(self):
    num_cities = 0
    for node in self.nodes:
      if node.building and node.building.type == BUILDING_TYPES.CITY:
        num_cities +=1
    return num_cities

  def get_roads(self):
    num_roads = 0
    for player in self.players:
      num_roads += len(player.roads)
    return num_roads

  def get_trades(self):
    num_trades = 0
    for player in self.players:
      num_trades += player.num_trades
    return num_trades

  def get_final_game(self):
    board_types = [tile.type.value for tile in self.board]
    board_values = [0 if tile.value is None else tile.value for tile in self.board]
    harbors = [str(node.harbor) if node.harbor else None for node in self.nodes]
    return {
      'board': {
        'types': board_types,
        'values': board_values,
        'harbors': harbors,
      },
      'players': [{
        'name': player.name,
        'color': player.color,
        'strategy': self.agents[idx].strategy,
        'winner': self.winner == self.agents[idx].id,
        'points': player.get_points(),
      } for idx, player in enumerate(self.players)],
      'turns': self.turn_data
    }

  def get_state(self, player):
    # Board types:
    # board_types = [y for x in [Board.type_to_input_arr(tile.type) for tile in self.board] for y in x]
    board_types = [Board.type_to_input_arr(tile.type) for tile in self.board]
    # Board values:
    board_values = Board.values_to_input_arr([0 if tile.value is None else tile.value for tile in self.board])

    # Buildings on nodes
    buildings = []
    for node in self.nodes:
      if not node.building:
        buildings.append(0)
      else:
        player_building = node.building.player.id == player.id
        # OLD
        # building_type = 0.5 if node.building.type == BUILDING_TYPES.VILLAGE else 1
        # buildings.append(0 + building_type if player_building else 0 - building_type)
        # New test
        building_type = 1 if node.building.type == BUILDING_TYPES.VILLAGE else 2
        buildings.append(2 + building_type if player_building else 0 + building_type)
    
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
              # OLD
              # roads.append(1)
              roads.append(2)
            else:
              # OLD
              # roads.append(-1)
              roads.append(1)
      if not found:
        roads.append(0)

    harbors = []
    for idx, node in enumerate(self.nodes):
      if not idx in harbor_nodes:
        continue
      if not node.harbor:
        harbors.append(0)
      elif node.harbor == HARBOR_TYPES.THREE_TO_ONE:
        harbors.append(1)
      elif node.harbor == HARBOR_TYPES.WHEAT:
        harbors.append(2)
      elif node.harbor == HARBOR_TYPES.BRICKS:
        harbors.append(3)
      elif node.harbor == HARBOR_TYPES.WOOD:
        harbors.append(4)
      elif node.harbor == HARBOR_TYPES.STONE:
        harbors.append(5)
      elif node.harbor == HARBOR_TYPES.SHEEP:
        harbors.append(6)
  
    cards = list(player.cards.values())

    return board_types + board_values + buildings + roads + harbors + cards