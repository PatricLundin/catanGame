from game.game import Game
from game.building import BUILDING_TYPES
from game.player import Player
import time

start_time = time.time()

for i in range(100):
  game = Game([])
  player = Player(game, 'test', 'asd')

  player.build_building(game.nodes[0])
  player.upgrade_building(game.nodes[0].building)

print("--- %s seconds ---" % (time.time() - start_time))
