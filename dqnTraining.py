from training.algorithms.reinforcement import ReinforcementAlgorithm
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

game_players = 3
num_games = 10000000
agents_per_game = 1
layers=[250, 150]

algoRunner = ReinforcementAlgorithm(game_players=game_players, agents_per_game=agents_per_game, layers=layers)
algoRunner.run(num_games)
