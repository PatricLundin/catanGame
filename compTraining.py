from training.genAlgo import GeneticAlgorithm
import time
import numpy as np
from datetime import datetime

curr_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
num_agents = 54
num_generations = 10
agents_per_game = 3

algoRunner = GeneticAlgorithm(num_generations=num_generations, pop_size=num_agents, agents_per_game=agents_per_game)
algoRunner.run_generations(1)