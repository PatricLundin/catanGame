import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
import numpy as np

class AllActionsModel:

  @staticmethod
  def get_model(layers):
    model = Sequential()
    for idx, layer in enumerate(layers):
      if idx == 0:
        model.add(Dense(units=layer, activation='relu', input_dim=264))
      else:
        model.add(Dense(units=layer, activation='relu'))
      model.add(BatchNormalization())
    model.add(Dense(units=201, activation='sigmoid'))
    return model

  @staticmethod
  def select_action(agent, actions):
    if agent.eps > np.random.random_sample():
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]
    input_vals = np.array([agent.game.get_state(agent.player)])
    predictions = agent.model.predict(input_vals, batch_size=None)
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
            l2.append(y if np.random.random_sample() < 0.5 else w2[layerIdx][xIdx][yIdx])
          l1.append(np.array(l2))
        else:
          l1.append(x if np.random.random_sample() < 0.5 else w2[layerIdx][xIdx])
      w3.append(np.array(l1))
    
    return w3