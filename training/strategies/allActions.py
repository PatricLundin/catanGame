import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
from keras import initializers, optimizers, losses
import numpy as np

MUTATION_RATE = 0.1

class AllActionsModel:

  @staticmethod
  def get_model(layers):
    model = Sequential()
    for idx, layer in enumerate(layers):
      if idx == 0:
        # model.add(Dense(units=layer, activation='relu', input_dim=264, bias_initializer=initializers.Constant(0.1)))
        model.add(Dense(units=layer, activation='relu', input_dim=264))
      else:
        # model.add(Dense(units=layer, activation='relu', bias_initializer=initializers.Constant(0.1)))
        model.add(Dense(units=layer, activation='relu'))
      model.add(BatchNormalization())
    model.add(Dense(units=201, activation='sigmoid'))
    model.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss=losses.MeanSquaredError())
    return model

  @staticmethod
  def select_action(game, agent, actions):
    if agent.eps > np.random.random_sample():
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]
    input_vals = np.array([game.get_state(game.players[game.current_turn])])
    predictions = agent.model.predict_on_batch(input_vals)
    sortedArgs = np.argsort(predictions[0])
    actionIdx = None
    for i in range(len(sortedArgs)):
      if actions[sortedArgs[i]] is not None:
        actionIdx = sortedArgs[i]
        break
    return actions[actionIdx]

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