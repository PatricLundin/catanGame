
class Tile:

  # Initializer / Instance Attributes
  def __init__(self, idx, type, value):
    xValues = [0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2]
    yValues = [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
    self.x = xValues[idx]
    self.y = yValues[idx]
    self.type = type
    self.value = value
    self.nodes = []

  def add_node(self, node):
    self.nodes.append(node)

  def distribute_cards(self):
    for node in self.nodes:
      if node.building:
        node.building.get_resources(self.type)

  def set_state(self, state):
    self.type = state['type']
    self.value = state['value']

  def get_state(self):
    return {
      'type': self.type,
      'value': self.value,
    }

  def __str__(self):
    return f'x: {self.x}, y: {self.y}, value: {self.value}, type: {self.type}'