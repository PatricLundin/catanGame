from game.game import Game
from game.building import BUILDING_TYPES
from game.player import Player
from game.agent import Agent
import time
import numpy as np

start_time = time.time()

agents = [Agent() for i in range(3)]
game = Game(agents)
game.run_game()

print("--- %s seconds ---" % (time.time() - start_time))
