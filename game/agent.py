import uuid
from enum import Enum
import numpy as np
from game.player import Actions
from training.strategies.allActions import AllActionsModel
from training.strategies.evaluate import EvaluateModel

class STRATEGIES(Enum):
  RANDOM = 0
  ALLACTIONS = 1
  EVALUATE = 2

INITIAL_EPS = 0.1
DECAY_FACTOR = 0.01

class Agent:

  # Initializer / Instance Attributes
  def __init__(self, strategy=STRATEGIES.RANDOM, layers=[100, 100]):
    self.id = str(uuid.uuid4())
    self.strategy = strategy
    self.layers = layers
    self.model = None
    self.eps = INITIAL_EPS
    self.steps = 0
    self.lossArr = []
    self.num_games = 0

    self.init_strategy()

  def init_strategy(self):
    if self.strategy == STRATEGIES.ALLACTIONS:
      self.model = AllActionsModel.get_model(self.layers)
    elif self.strategy == STRATEGIES.EVALUATE:
      self.model = EvaluateModel.get_model(self.layers)

  def select_action(self, game, actions):
    if self.strategy == STRATEGIES.RANDOM:
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]
    elif self.strategy == STRATEGIES.ALLACTIONS:
      return AllActionsModel.select_action(game, self, actions)
    elif self.strategy == STRATEGIES.EVALUATE:
      return EvaluateModel.select_action(game, self, actions)

  def choose_starting_village(self, player):
      village_actions = player.get_starting_building_actions()
      action = self.select_action(player.game, village_actions)
      player.take_action(action)

      road_actions = player.get_starting_road_actions(player.game.nodes[action[1]])
      action = self.select_action(player.game, road_actions)
      player.take_action(action)

  def turn(self, player):
    while True:
      self.steps += 1
      self.eps = INITIAL_EPS * (1 - DECAY_FACTOR) ** self.steps
      actions = player.get_all_actions()
      action = self.select_action(player.game, actions)
      player.take_action(action)
      if action[0] == Actions.NOACTION:
        break

  def mix_weights(self, model, layers):
    if self.strategy == STRATEGIES.ALLACTIONS:
      mixed_weights = AllActionsModel.mix_weights(self.model, model)
      agent = Agent(strategy=STRATEGIES.ALLACTIONS, layers=layers)
      agent.model.set_weights(mixed_weights)
      return agent
    elif self.strategy == STRATEGIES.EVALUATE:
      mixed_weights = EvaluateModel.mix_weights(self.model, model)
      agent = Agent(strategy=STRATEGIES.EVALUATE, layers=layers)
      agent.model.set_weights(mixed_weights)
      return agent

  def __str__(self):
    return f'id: {self.id}, strategy: {self.strategy}, steps {self.steps}, games: {self.num_games}'

  def __eq__(self, other):
    if isinstance(other, Agent):
      return self.id == other.id
    else:
      return self.id == other