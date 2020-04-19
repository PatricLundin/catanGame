from game.game import Game
from game.board import Board, GRID_TYPES
from game.agent import Agent, STRATEGIES
import time
import numpy as np

start_time = time.time()

agents = [Agent(STRATEGIES.RANDOM) for i in range(3)]
game = Game(agents)
game.choose_starting_villages()

for turn in range(100):
  game.turn()

game.num_turns += 1
game.current_turn = (game.current_turn + 1) % len(game.players)
game.dice_roll = game.roll_dice()
game.distribute_cards()
actions = game.players[game.current_turn].get_actions()

print('Actions length:', len(actions))

MAX_TIMES = 100
times = [0] * MAX_TIMES

for i in range(1000):
  for idx, action in enumerate(actions):
    start_sim_time = time.time()
    game.simulateAction(action)
    times[(i * len(actions) + idx) % MAX_TIMES] = time.time() - start_sim_time
  if i % 100 == 0:
    print('Aveage time:', np.sum(times) / MAX_TIMES)

  # game_states = [game.get_state(player) for player in game.players]
  # game_states_post = [game.get_state(player) for player in game.players]
  # print('Original is same')
  # for idx, o_state in enumerate(game_states):
  #   np.testing.assert_array_equal(o_state, game_states_post[idx])
  # print('Copy is same')
  # g_sim_states = [g_sim.get_state(player) for player in g_sim.players]
  # for idx, sim_state in enumerate(g_sim_states):
  #   try:
  #     np.testing.assert_array_equal(sim_state, game_states[idx])
  #   except AssertionError as err:
  #     print(err)
  #     for ix, v1 in enumerate(sim_state):
  #       if v1 != game_states[idx][ix]:
  #         print('idx', ix, ', original:', game_states[idx][ix], 'Sim: ', v1)


print("--- %s seconds ---" % (time.time() - start_time))
