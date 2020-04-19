from training.algorithms.genAlgo import GeneticAlgorithm
import time
import numpy as np
from datetime import datetime
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Restrict TensorFlow to only use the fourth GPU
        tf.config.experimental.set_visible_devices(gpus[0], 'GPU')

        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

num_agents = 54 # 54, 18
num_generations = 10000
agents_per_game = 3
layers=[100, 20]

algoRunner = GeneticAlgorithm(pop_size=num_agents, agents_per_game=agents_per_game, layers=layers)
algoRunner.run_generations(num_generations)
