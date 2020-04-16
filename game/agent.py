import uuid
from enum import Enum
import numpy as np
from game.player import Actions

class STRATEGIES(Enum):
  RANDOM = 0

INITIAL_EPS = 0.1
DECAY_FACTOR = 0.01

class Agent:

  # Initializer / Instance Attributes
  def __init__(self, strategy = STRATEGIES.RANDOM):
    self.id = str(uuid.uuid4())
    self.strategy = strategy
    self.eps = INITIAL_EPS
    self.steps = 0
    self.lossArr = []
    self.player = None
    self.game = None

  def set_player(self, player):
    self.player = player
    self.game = player.game

  def clear_player(self):
    self.player = None
    self.game = None

  def select_action(self, actions):
    if self.strategy == STRATEGIES.RANDOM:
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]

  def choose_starting_village(self):
      village_actions = self.player.get_starting_building_actions()
      action = self.select_action(village_actions)
      self.player.take_action(action)

      road_actions = self.player.get_starting_road_actions(self.game.nodes[action[1]])
      action = self.select_action(road_actions)
      self.player.take_action(action)

  def turn(self):
    while True:
      self.steps += 1
      self.eps = INITIAL_EPS * (1 - DECAY_FACTOR) ** self.steps
      actions = self.player.get_all_actions()
      action = self.select_action(actions)
      self.player.take_action(action)
      if action[0] == Actions.NOACTION:
        break
      

  def __str__(self):
    return f'id: {self.id}, strategy: {self.strategy}, steps {self.steps}, eps: {self.eps}'