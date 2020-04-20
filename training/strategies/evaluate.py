import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
from keras import initializers
import numpy as np
import time

MUTATION_RATE = 0.1
NUM_SIMS = 3
NUM_EXPLORE = 2

class EvaluateModel:

  @staticmethod
  def get_model(layers):
    model = Sequential()
    for idx, layer in enumerate(layers):
      if idx == 0:
        model.add(Dense(units=layer, activation='relu', input_dim=264, bias_initializer=initializers.Constant(0.1)))
      else:
        model.add(Dense(units=layer, activation='relu', bias_initializer=initializers.Constant(0.1)))
      model.add(BatchNormalization())
    model.add(Dense(units=1, activation='tanh'))
    return model

  @staticmethod
  def select_actionSim(game, agent, actions):
    available_actions = list(filter(lambda a: a is not None, actions))
    if agent.eps > np.random.random_sample():
      np.random.shuffle(available_actions)
      return available_actions[0]
    # start_time = time.time()
    new_states = [game.simulateAction(action) for action in available_actions]
    # print("--- simulate all actions %s took %s seconds ---" % (len(available_actions), time.time() - start_time))
    # start_time = time.time()
    predictions = agent.model.predict_on_batch(np.array(new_states))
    predictions = [p[0] for p in predictions]
    # print("--- predictions %s took %s seconds ---" % (len(available_actions), time.time() - start_time))
    # predictions = []
    # for state in new_states:
    #   predictions.append(agent.model.predict_on_batch(np.array([state])))
    best_actions = np.argsort(predictions)
    if not len(best_actions) == 1:
      best = None
      sims = []
      for action in best_actions[:NUM_EXPLORE]:
        winners = { 'agent': 0, 'other': 0 }
        # print('action', available_actions[action])
        for _ in range(NUM_SIMS):
          w = game.simulateGame(available_actions[action])
          if w == agent.id:
            winners['agent'] += 1
          else:
            winners['other'] += 1
        if len(sims) == 0:
          best = action
        elif len(sims) > 0 and not any([s['agent'] >= winners['agent'] for s in sims]):
          best = action
        sims.append(winners)
      # print(sims)
      # print(best)
      return available_actions[best]
    else:
      return available_actions[best_actions[0]]
    # best_action = np.argmax(predictions)
    # return available_actions[best_action]

  @staticmethod
  def select_action(game, agent, actions):
    available_actions = list(filter(lambda a: a is not None, actions))
    if agent.eps > np.random.random_sample():
      np.random.shuffle(available_actions)
      return available_actions[0]
    # start_time = time.time()
    new_states = [game.simulateAction(action) for action in available_actions]
    # print("--- simulate all actions %s took %s seconds ---" % (len(available_actions), time.time() - start_time))
    # start_time = time.time()
    predictions = agent.model.predict_on_batch(np.array(new_states))
    best_action = np.argmax(predictions)
    return available_actions[best_action]

  @staticmethod
  def mix_weights(model1, model2):
    w1 = model1.model.get_weights()
    w2 = model2.model.get_weights()
    w3 = []
    for layerIdx, layer in enumerate(w1):
      l1 = []
      for xIdx, x in enumerate(layer):
        if hasattr(x, "__len__"):
          l2 = []
          for yIdx, y in enumerate(x):
            if np.random.random_sample() < MUTATION_RATE:
              l2.append(np.random.random_sample() * 0.1 - 0.05)
            else:
              l2.append(y if np.random.random_sample() < 0.5 else w2[layerIdx][xIdx][yIdx])
          l1.append(np.array(l2))
        else:
          if np.random.random_sample() < MUTATION_RATE:
            l1.append(0 if x == 1 else 1)
          else:
            l1.append(x if np.random.random_sample() < 0.5 else w2[layerIdx][xIdx])
      w3.append(np.array(l1))
    
    return w3