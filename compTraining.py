from training.genAlgo import GeneticAlgorithm
import time
import numpy as np
from datetime import datetime

curr_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
num_agents = 54
num_generations = 10000
agents_per_game = 3

algoRunner = GeneticAlgorithm(pop_size=num_agents, agents_per_game=agents_per_game)
algoRunner.run_generations(num_generations)
