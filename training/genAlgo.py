from game.agent import STRATEGIES, Agent
import numpy as np

class GeneticAlgorithm():

  def __init__(self, num_generations=10000, pop_size=54, agents_per_game=3):
    self.agents_per_game = agents_per_game
    self.pop_size = pop_size
    self.num_generations = num_generations
    self.population = []
    self.generations = 0

    self.init_population()
  
  def init_population(self):
    available_strategies = [strategy for strategy in STRATEGIES if strategy is not STRATEGIES.RANDOM]

    for _ in range(self.pop_size):
      strategy = np.random.choice(available_strategies)
      self.population.append(Agent(strategy))

  def run_game(self, game_index):
    agents = self.population[game_index*self.agents_per_game:self.agents_per_game+self.agents_per_game*game_index]
    print(agents)

  def run_generations(self, n):
    for _ in range(n):
      self.generations += 1
      np.random.shuffle(self.population)
      print(self.pop_size)
      print(self.agents_per_game)
      print (round(self.pop_size / self.agents_per_game))
      print (int(round(self.pop_size / self.agents_per_game)))
      for game_index in range(int(round(self.pop_size / self.agents_per_game))):
        self.run_game(game_index)