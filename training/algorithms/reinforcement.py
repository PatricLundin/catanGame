from game.agent import STRATEGIES, Agent
from game.game import Game
from game.building import BUILDING_TYPES
from training.strategies.allActions import AllActionsModel
from datetime import datetime
from keras.models import load_model
import time
import numpy as np
import tensorflow as tf
import os
import keras.backend as K
import copy

save_interval = 1000
update_freq = 200
DECAY_FACTOR = 0.0002
NOACTION_MEMORY = 0.05

class MemoryBuffer():
  def __init__(self, max_size, input_shape):
    self.mem_size = max_size
    self.mem_counter = 0

    self.state_memory = np.zeros((self.mem_size, *input_shape), dtype=np.float32)
    self.new_state_memory = np.zeros((self.mem_size, *input_shape), dtype=np.float32)
    self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
    self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
    self.terminal_memory = np.zeros(self.mem_size, dtype=bool)

  def store_transition(self, state, action, reward, next_state, done):
    index = self.mem_counter % self.mem_size
    self.state_memory[index] = state
    self.new_state_memory[index] = next_state
    self.action_memory[index] = action
    self.reward_memory[index] = reward
    self.terminal_memory[index] = done

    self.mem_counter += 1

  def sample_buffer(self, buffer_size):
    max_mem = min(self.mem_counter, self.mem_size)
    batch = np.random.choice(max_mem, buffer_size, replace=False)

    states = self.state_memory[batch]
    new_states = self.new_state_memory[batch]
    actions = self.action_memory[batch]
    rewards = self.reward_memory[batch]
    dones = self.terminal_memory[batch]
    return states, new_states, actions, rewards, dones


class ReinforcementAlgorithm():

  def __init__(self, agents_per_game=1, layers=[100, 100], game_players=3):
    self.agents_per_game = agents_per_game
    self.layers = layers
    self.game_players = game_players
    self.games_played = 0
    self.agents = []
    self.current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")
    log_dir = 'logs/reinforcement/' + self.current_time
    try:
      os.makedirs(log_dir)
    except FileExistsError:
      pass
    self.summary_writer = tf.summary.create_file_writer(log_dir)
    self.memory = MemoryBuffer(max_size=30000, input_shape=[199])
    # self.average_reward_last_target = np.zeros(update_freq, dtype=np.float32)
    # self.average_reward_current_model = np.zeros(update_freq, dtype=np.float32)

    self.init_population()
  
  def init_population(self):
    # available_strategies = [strategy for strategy in STRATEGIES if strategy is not STRATEGIES.RANDOM]
    available_strategies = [STRATEGIES.ALLACTIONS]

    for _ in range(self.agents_per_game):
      strategy = np.random.choice(available_strategies)
      self.agents.append(Agent(strategy=strategy, layers=self.layers))
    
    for _ in range(self.game_players - self.agents_per_game):
      self.agents.append(Agent(strategy=STRATEGIES.RANDOM))

  def run_game(self):
    game = Game(self.agents)
    game.run_game()

    num_memory = 0
    for idx, agent in enumerate(self.agents):
      if not agent.strategy == STRATEGIES.RANDOM:
        mem = agent.get_memory(game.winner, game.players[idx], True)
        num_memory = len(mem)
        for data in mem:
          state, action, reward, next_state, done, turn_idx = data
          if not action == 0 or np.random.random_sample() < NOACTION_MEMORY:
            # print(f'action {action}, reward: {reward}')
            self.memory.store_transition(state=state, action=action, reward=reward, next_state=next_state, done=done)

    game_time = game.time
    turns = game.num_turns
    winner = self.agents[self.agents.index(game.winner)]
    villages = len(game.players[0].buildings)
    cities = np.sum([1 if b.type == BUILDING_TYPES.CITY else 0 for b in game.players[0].buildings])
    roads = len(game.players[0].roads)
    trades = game.players[0].num_trades
    points = game.players[0].get_points()
    return game_time, turns, winner, villages, cities, roads, trades, points, num_memory

  def run(self, n):
    average_over = 100

    game_times = [0] * average_over
    game_turns = [0] * average_over
    game_villages = [0] * average_over
    game_cities = [0] * average_over
    game_roads = [0] * average_over
    game_trades = [0] * average_over
    game_winner = [0] * average_over
    game_points = [0] * average_over
    game_memory_count = [0] * average_over
    # num_replace_network = 0

    for i in range(n):
      start_time = time.time()
      game_time, turns, winner, villages, cities, roads, trades, points, num_memory = self.run_game()
      game_times[i % average_over] = game_time
      game_turns[i % average_over] = turns
      game_villages[i % average_over] = villages
      game_cities[i % average_over] = cities
      game_roads[i % average_over] = roads
      game_trades[i % average_over] = trades
      game_winner[i % average_over] = winner.strategy != STRATEGIES.RANDOM
      game_points[i % average_over] = points
      game_memory_count[i % average_over] = num_memory

      # test target model updaing
      # self.average_reward_current_model[(i + 1) % update_freq] = points * (1 - self.agents[0].eps)

      # Logging data
      average_game_time = np.sum(game_times) / min(i + 1, len(game_times))
      average_game_turns = np.sum(game_turns) / min(i + 1, len(game_turns))
      average_villages = np.sum(game_villages) / min(i + 1, len(game_villages))
      average_cities = np.sum(game_cities) / min(i + 1, len(game_cities))
      average_roads = np.sum(game_roads) / min(i + 1, len(game_roads))
      average_trades = np.sum(game_trades) / min(i + 1, len(game_trades))
      average_wins = np.sum(game_winner) / min(i + 1, len(game_winner))
      average_points = np.sum(game_points) / min(i + 1, len(game_points))
      average_mem_count = np.sum(game_memory_count) / min(i + 1, len(game_memory_count))

      print('------ Game', i + 1, '------ time: %s' % (time.time() - start_time))
      print('Average points', average_points)

      # training
      if (i + 1) % 1 == 0 and i > 50:
        for agent in self.agents:
          if agent.strategy != STRATEGIES.RANDOM and self.memory.mem_counter > agent.batch_size:
            states, new_states, actions, rewards, dones = self.memory.sample_buffer(agent.batch_size)

            # print(f'action {actions[0]}, reward: {rewards[0]}, done: {dones[0]}')
            # print('State')
            # vals = []
            # for val in states[0]:
            #   if len(vals) == 6:
            #     print(vals)
            #     vals = []
            #   vals.append(val) 
            
            # print('Next_State')
            # vals = []
            # for val in new_states[0]:
            #   if len(vals) == 6:
            #     print(vals)
            #     vals = []
            #   vals.append(val) 

            # Target network code
            # print('current', np.sum(self.average_reward_current_model))
            # vals = []
            # for val in self.average_reward_current_model:
            #   if len(vals) == 15:
            #     print(vals)
            #     vals = []
            #   vals.append(val)
            # print(vals)
            
            # print('target', np.sum(self.average_reward_last_target))
            # vals = []
            # for val in self.average_reward_last_target:
            #   if len(vals) == 15:
            #     print(vals)
            #     vals = []
            #   vals.append(val)
            # print(vals)
            if (i + 1) % update_freq == 0:
              agent.update_target_model()
              # if np.sum(self.average_reward_current_model) > np.sum(self.average_reward_last_target):
              #   agent.update_target_model()
              #   self.average_reward_last_target = np.copy(self.average_reward_current_model)
              #   num_replace_network += 1
              # else:
              #   agent.reload_target_model()

            q_eval = agent.model.predict_on_batch(states)
            q_next = agent.target_model.predict_on_batch(new_states)

            q_next[dones] = 0.0

            # print('q_eval[0][actions[0]]', q_eval[0][actions[0]])
            # print('q_next', q_next[0])

            indicies = np.arange(agent.batch_size)
            q_target = copy.deepcopy(q_eval)

            # print('q_target[0][actions[0]]', q_target[0][actions[0]])
            q_target[indicies, actions] = rewards + agent.gamma * np.max(q_next, axis=1)
            # print('q_eval[0][actions[0]]', q_eval[0][actions[0]])
            # print('q_target[0][actions[0]]', q_target[0][actions[0]])
            # print('new val', rewards[0] + agent.gamma * np.max(q_next[0]))

            # print('new val', rewards[0] + agent.gamma * np.max(q_next[0]))
            # vals = []
            # for val in q_target[0] - q_eval[0]:
            #   if len(vals) == 10:
            #     print(vals)
            #     vals = []
            #   vals.append(val) 

            # print('q_target', q_target[0])

            training_loss = agent.model.train_on_batch(states, q_target)

            agent.eps = max(agent.eps * (1 - DECAY_FACTOR), agent.eps_min)

            with self.summary_writer.as_default():
              tf.summary.scalar('Training loss', training_loss, step=i + 1)

      with self.summary_writer.as_default():
        tf.summary.scalar('Average game time', average_game_time, step=i + 1)
        tf.summary.scalar('Average game turns', average_game_turns, step=i + 1)
        tf.summary.scalar('Average villages', average_villages, step=i + 1)
        tf.summary.scalar('Average cities', average_cities, step=i + 1)
        tf.summary.scalar('Average roads', average_roads, step=i + 1)
        tf.summary.scalar('Average trades', average_trades, step=i + 1)
        tf.summary.scalar('_Average wins', average_wins, step=i + 1)
        tf.summary.scalar('Agent eps', self.agents[0].eps, step=i + 1)
        tf.summary.scalar('_Agent points', average_points, step=i + 1)
        tf.summary.scalar('Agent memory count', average_mem_count, step=i + 1)
        # tf.summary.scalar('Replace network', num_replace_network, step=i + 1)

      # Saving models
      if (i + 1) % save_interval == 0:
        save_path = 'models/reinforcement/' + str(i + 1) + '/' + self.current_time
        try:
          os.makedirs(save_path)
        except FileExistsError:
          pass
        self.agents[0].model.save(save_path + '/model' + str(self.layers).replace(" ", ""))
        del self.agents[0].model
        K.clear_session()
        self.agents[0].model = load_model(save_path + '/model' + str(self.layers).replace(" ", ""))

