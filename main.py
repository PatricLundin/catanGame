from game.game import Game
from game.board import Board, GRID_TYPES
from game.agent import Agent, STRATEGIES
import time
import numpy as np
import multiprocessing as mp

start_time = time.time()

# output = mp.Queue()

# def run_game(num_agents, out):
#   np.random.seed()
#   agents = [Agent) for i in range(num_agents)]
#   game = Game(agents)
#   game.run_game()
#   out.put((game.time, game.num_turns))

# # Setup a list of processes that we want to run
# processes = [mp.Process(target=run_game, args=(3, output)) for x in range(10)]

# # Run processes
# for p in processes:
#     p.start()

# # Exit the completed processes
# for p in processes:
#     p.join()

# # Get process results from the output queue
# results = [output.get() for p in processes]

# for game_time, num_turns in results:
#   game_times.append(game_time)
#   game_turns.append(num_turns)

for x in range(100):
  agents = [Agent(STRATEGIES.RANDOM) for i in range(54)]
  game_turns = []
  game_times = []
  for i in range(18):
    game = Game(agents[i*3:3+i*3])
    game.run_game()
    game_times.append(game.time)
    game_turns.append(game.num_turns)

  print('Average time', np.sum(game_times) / len(game_times))
  print('Average turns', np.sum(game_turns) / len(game_turns))

print("--- %s seconds ---" % (time.time() - start_time))
