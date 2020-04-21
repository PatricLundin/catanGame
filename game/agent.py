import uuid
from enum import Enum
import numpy as np
from game.player import Actions
from training.strategies.allActions import AllActionsModel
from training.strategies.evaluate import EvaluateModel
import time

class STRATEGIES(Enum):
  RANDOM = 0
  ALLACTIONS = 1
  EVALUATE = 2

class Agent:

  # Initializer / Instance Attributes
  def __init__(self, strategy=STRATEGIES.RANDOM, layers=[100, 100], gamma=0.99, \
              eps=1.0, batch_size=50, eps_dec=0.01, eps_min=0.01):
    self.id = str(uuid.uuid4())
    self.strategy = strategy
    self.layers = layers
    self.eps = eps
    self.eps_dec = eps_dec
    self.eps_min = eps_min
    self.gamma = gamma
    self.batch_size = batch_size
    self.model = None
    self.steps = 0
    self.lossArr = []
    self.num_games = 0
    self.turn_data = []
    self.to_return = []

    self.init_strategy()

  def init_strategy(self):
    if self.strategy == STRATEGIES.ALLACTIONS:
      self.model = AllActionsModel.get_model(self.layers)
      self.target_model = AllActionsModel.get_model(self.layers)
    elif self.strategy == STRATEGIES.EVALUATE:
      self.model = EvaluateModel.get_model(self.layers)
      self.target_model = EvaluateModel.get_model(self.layers)

  def get_memory(self):
    to_return = self.to_return
    self.to_return = []
    return to_return

  def update_target_model(self):
    if not self.strategy == STRATEGIES.RANDOM:
      self.target_model.set_weights(self.model.get_weights())

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

      road_actions = player.get_starting_road_actions(player.game.nodes[action[2]])
      action = self.select_action(player.game, road_actions)
      player.take_action(action)

  def turn(self, player):
    while True:
      self.steps += 1
      actions = player.get_all_actions()
      # start_time = time.time()
      state = player.game.get_state(player)
      action = self.select_action(player.game, actions)
      # if not self.strategy == STRATEGIES.RANDOM:
        # print("--- action selection %s seconds ---" % (time.time() - start_time))
      player.take_action(action)
      next_state = player.game.get_state(player)
      done = player.get_points() == 10

      def get_reward():
        if action[1] == Actions.BUILDING or action[1] == Actions.UPGRADE:
          return 0 if done else 1
        else:
          return 0
      reward = get_reward()

      data = [state, action[0], reward, next_state, done]
      if reward == 1 or done:
        if len(self.to_return) > 3000:
          self.to_return = []
        self.to_return.append(tuple(data))
        for idx, turn in enumerate(list(reversed(self.turn_data))):
          turn[2] = 1 / (idx + 2)
          self.to_return.append(tuple(turn))
        self.turn_data = []
      else:
        self.turn_data.append(data)

      if action[1] == Actions.NOACTION:
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