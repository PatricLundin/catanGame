from game.agent import STRATEGIES, Agent
from game.game import Game
from training.strategies.allActions import AllActionsModel
from datetime import datetime
from keras.models import load_model
import time
import numpy as np
import tensorflow as tf
import os
import keras.backend as K
import multiprocessing as mp

save_interval = 5

class GeneticAlgorithm():

  def __init__(self, pop_size=54, agents_per_game=3, layers=[100, 100]):
    self.agents_per_game = agents_per_game
    self.pop_size = pop_size
    self.layers = layers
    self.population = []
    self.generations = 0
    self.current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")
    log_dir = 'logs/genetic/' + self.current_time
    try:
      os.makedirs(log_dir)
    except FileExistsError:
      pass
    self.summary_writer = tf.summary.create_file_writer(log_dir)

    self.init_population()
  
  def init_population(self):
    available_strategies = [strategy for strategy in STRATEGIES if strategy is not STRATEGIES.RANDOM]

    for _ in range(self.pop_size):
      strategy = np.random.choice(available_strategies)
      self.population.append(Agent(strategy=strategy, layers=self.layers))

  @staticmethod
  def run_game(agents_data, out):
    agents = []
    for a_d in agents_data:
      agent = Agent(strategy=a_d['strategy'], layers=a_d['layers'])
      agent.id = a_d['id']
      agent.model.set_weights(a_d['weights'])
      agents.append(agent)
    game = Game(agents)
    game.run_game()
    out.put(game.time, game.num_turns, game.winner)

  def run_generations(self, n):
    for _ in range(n):
      start_time = time.time()
      self.generations += 1
      np.random.shuffle(self.population)
      game_times = []
      game_turns = []
      winners = []

      output = mp.Queue()

      processes = []
      for game_index in range(int(round(self.pop_size / self.agents_per_game))):
        agents = self.population[game_index*self.agents_per_game:self.agents_per_game+self.agents_per_game*game_index]
        agents_data = []
        for agent in agents:
          data = {
            'strategy': agent.strategy,
            'layers': self.layers,
            'id': agent.id,
            'weights': agent.model.get_weights(),
          }
          agents_data.append(data)
        processes.append(mp.Process(target=GeneticAlgorithm.run_game, args=(agents_data, output)))

      # # Run processes
      for p in processes:
          p.start()

      # # Exit the completed processes
      for p in processes:
          p.join()

      # # Get process results from the output queue
      results = [output.get() for p in processes]

      for game_time, num_turns, winner in results:
        game_times.append(game_time)
        game_turns.append(num_turns)
        winners.append(self.population[self.population.index(winner)])
      
      # # Run games
      # for game_index in range(int(round(self.pop_size / self.agents_per_game))):
      #   game_time, turns, winner = self.run_game(game_index)
      #   game_times.append(game_time)
      #   game_turns.append(turns)
      #   winners.append(winner)

      # Saving models
      if self.generations % save_interval == 0:
        save_path = 'models/genetic/' + str(self.generations) + '/' + self.current_time
        os.makedirs(save_path)
        for idx, agent in enumerate(winners):
          agent.model.save(save_path + '/model' + str(idx))

        for agent in self.population:
          del agent.model
        K.clear_session()
        for idx, agent in enumerate(winners):
          agent.model = load_model(save_path + '/model' + str(idx))
      else: # need to remove models to same memory
        def pred_losers(a):
          try:
            if winners.index(a):
              return False
          except ValueError:
            True
        losers = list(filter(pred_losers, self.population))
        for loser in losers:
          del loser.model

      # Recreate population
      self.population = winners

      while len(self.population) < self.pop_size:
        for w1 in winners:
          for w2 in winners:
            if len(self.population) < self.pop_size and not w1 == w2:
              new_agent = w1.mix_weights(w2)
              self.population.append(new_agent)

      # Logging 
      average_game_time = np.sum(game_times) / len(game_times)
      average_game_turns = np.sum(game_turns) / len(game_turns)
      print('------ Generation', self.generations, '------ time: %s' % (time.time() - start_time))
      print('Average time', average_game_time)
      print('Average turns', average_game_turns)
      with self.summary_writer.as_default():
        tf.summary.scalar('Average game time', average_game_time, step=self.generations)
        tf.summary.scalar('Average game turns', average_game_turns, step=self.generations)


if __name__ == '__main__':
  num_agents = 54
  num_generations = 10000
  agents_per_game = 3

  algoRunner = GeneticAlgorithm(pop_size=num_agents, agents_per_game=agents_per_game)
  algoRunner.run_generations(num_generations)