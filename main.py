from game.game import Game
from game.building import BUILDING_TYPES
from game.player import Player
from game.agent import Agent
import time
import numpy as np

game_turns = []
game_times = []

start_time = time.time()

agents = [Agent() for i in range(3)]
for i in range(100):
  game = Game(agents)
  game.run_game()
  game_times.append(game.time)
  game_turns.append(game.num_turns)

print('Average time', np.sum(game_times) / len(game_times))
print('Average turns', np.sum(game_turns) / len(game_turns))

print("--- %s seconds ---" % (time.time() - start_time))
