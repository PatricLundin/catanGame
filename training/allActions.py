import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
import numpy as np

class AllActionsModel:

  @staticmethod
  def get_model():
    model = Sequential()
    model.add(Dense(units=100, activation='relu', input_dim=169))
    model.add(BatchNormalization())
    model.add(Dense(units=100, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dense(units=201, activation='sigmoid'))
    return model

  @staticmethod
  def select_action(agent, actions):
    if agent.eps > np.random.random_sample():
      filtered = list(filter(lambda a: a is not None, actions))
      np.random.shuffle(filtered)
      return filtered[0]
    predictions = agent.model.predict(agent.game.get_state(agent.player), batch_size=None)
    sortedArgs = np.argsort(predictions)
    print(sortedArgs)

    filtered = list(filter(lambda a: a is not None, actions))
    np.random.shuffle(filtered)
    return filtered[0]