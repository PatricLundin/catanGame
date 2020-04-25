import uuid
from enum import Enum
import numpy as np
from game.player import Actions
from game.enums import STRATEGIES
from training.strategies.allActions import AllActionsModel
from training.strategies.evaluate import EvaluateModel
import time

BUILDING_REWARD = 1
USE_GAME_REWARD = True
REWARD_EQ = False

class Agent:

  # Initializer / Instance Attributes
  def __init__(self, strategy=STRATEGIES.RANDOM, layers=[100, 100], gamma=0.98, \
              eps=1.0, batch_size=20, eps_dec=0.01, eps_min=0.1):
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

  def get_memory(self, winnerId, player, clear):
    if not USE_GAME_REWARD:
      to_return = self.to_return
      if clear:
        self.to_return = []
      return to_return
    else:
      sign = -1
      if winnerId == self.id:
        sign = 1
      def reward(v):
        if REWARD_EQ:
          return - ((v / (4 * player.num_actions)) - 0.5)
        return 1
      to_return = []
      for idx, turn in enumerate(list(reversed(self.turn_data))):
        # turn[2] = 1 / (idx + 4)
        if turn[2] == 0:
          turn[2] = sign * reward(idx)
        # print('action', player.actionId_to_action(turn[1]), 'reward', turn[2])
        to_return.append(tuple(turn))
      if clear:
        self.turn_data = []
      return to_return

  def update_target_model(self):
    if not self.strategy == STRATEGIES.RANDOM:
      self.target_model.set_weights(self.model.get_weights())
  
  def reload_target_model(self):
    if not self.strategy == STRATEGIES.RANDOM:
      self.model.set_weights(self.target_model.get_weights())

  def select_action(self, game, actions):
    if self.strategy == STRATEGIES.RANDOM:
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]
    elif self.strategy == STRATEGIES.ALLACTIONS:
      return AllActionsModel.select_action(game, self, actions)
    elif self.strategy == STRATEGIES.EVALUATE:
      return EvaluateModel.select_action(game, self, actions)

  def save_turn_data(self, state, action, reward, next_state, done, num_turns):
    data = [state, action[0], reward, next_state, done, num_turns]
    if not USE_GAME_REWARD:
      if reward == BUILDING_REWARD or done:
        if len(self.to_return) > 3000:
          self.to_return = []
        self.to_return.append(tuple(data))
        for idx, turn in enumerate(list(reversed(self.turn_data))):
          turn[2] = 1 / (idx + 4)
          self.to_return.append(tuple(turn))
        self.turn_data = []
      else:
        self.turn_data.append(data)
    else:
      self.turn_data.append(data)
    return data

  def choose_starting_village(self, player):
      village_actions = player.get_starting_building_actions()
      action = self.select_action(player.game, village_actions)
      player.take_action(action)

      road_actions = player.get_starting_road_actions(player.game.nodes[action[2]])
      action = self.select_action(player.game, road_actions)
      player.take_action(action)

  def turn(self, player, num_turns):
    steps_this_turn = 0
    t_data = []
    while True:
      steps_this_turn += 1
      self.steps += 1
      actions = player.get_all_actions()

      if len(player.filter_available_actions(actions)) == 1: # only no nothing
        break

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
          return 0 if done else BUILDING_REWARD
        else:
          return 0
      data = self.save_turn_data(state, action, get_reward(), next_state, done, num_turns + steps_this_turn *0.01)
      t_data.append(data)
      # reward = get_reward()
      # data = [state, action[0], reward, next_state, done, num_turns + steps_this_turn *0.01]
      # if not USE_GAME_REWARD:
      #   if reward == BUILDING_REWARD or done:
      #     if len(self.to_return) > 3000:
      #       self.to_return = []
      #     self.to_return.append(tuple(data))
      #     for idx, turn in enumerate(list(reversed(self.turn_data))):
      #       turn[2] = 1 / (idx + 4)
      #       self.to_return.append(tuple(turn))
      #     self.turn_data = []
      #   else:
      #     self.turn_data.append(data)
      # else:
      #   self.turn_data.append(data)

      if action[1] == Actions.NOACTION:
        break
    return t_data

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