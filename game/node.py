import uuid

nodeIdxToNodePos = [
  [ 2, 0 ],
  [ 3, 0 ],
  [ 4, 0 ],
  [ 5, 0 ],
  [ 6, 0 ],
  [ 7, 0 ],
  [ 8, 0 ],
  [ 1, 1 ],
  [ 2, 1 ],
  [ 3, 1 ],
  [ 4, 1 ],
  [ 5, 1 ],
  [ 6, 1 ],
  [ 7, 1 ],
  [ 8, 1 ],
  [ 9, 1 ],
  [ 0, 2 ],
  [ 1, 2 ],
  [ 2, 2 ],
  [ 3, 2 ],
  [ 4, 2 ],
  [ 5, 2 ],
  [ 6, 2 ],
  [ 7, 2 ],
  [ 8, 2 ],
  [ 9, 2 ],
  [ 10, 2 ],
  [ 0, 3 ],
  [ 1, 3 ],
  [ 2, 3 ],
  [ 3, 3 ],
  [ 4, 3 ],
  [ 5, 3 ],
  [ 6, 3 ],
  [ 7, 3 ],
  [ 8, 3 ],
  [ 9, 3 ],
  [ 10, 3 ],
  [ 1, 4 ],
  [ 2, 4 ],
  [ 3, 4 ],
  [ 4, 4 ],
  [ 5, 4 ],
  [ 6, 4 ],
  [ 7, 4 ],
  [ 8, 4 ],
  [ 9, 4 ],
  [ 2, 5 ],
  [ 3, 5 ],
  [ 4, 5 ],
  [ 5, 5 ],
  [ 6, 5 ],
  [ 7, 5 ],
  [ 8, 5 ],
]

nodeToHex = [
  [0], # 2, 0
  [0], # 3, 0
  [0, 1], # 4, 0
  [1], # 5, 0
  [1, 2], # 6, 0
  [2], # 7, 0
  [2], # 8, 0
  [3], # 1, 1
  [0, 3], # 2, 1
  [0, 3, 4], # 3, 1
  [0, 1, 4], # 4, 1
  [1, 4, 5], # 5, 1
  [1, 2, 5], # 6, 1
  [2, 5, 6], # 7, 1
  [2, 6], # 8, 1
  [6], # 9, 1
  [7], # 0, 2
  [3, 7], # 1, 2
  [3, 7, 8], # 2, 2
  [3, 4, 8], # 3, 2
  [4, 8, 9], # 4, 2
  [4, 5, 9], # 5, 2
  [5, 9, 10], # 6, 2
  [5, 6, 10], # 7, 2
  [6, 10, 11], # 8, 2
  [6, 11], # 9, 2
  [11], # 10, 2
  [7], # 0, 3
  [7, 12], # 1, 3
  [7, 8, 12], # 2, 3
  [8, 12, 13], # 3, 3
  [8, 9, 13], # 4, 3
  [9, 13, 14], # 5, 3
  [9, 10, 14], # 6, 3
  [10, 14, 15], # 7, 3
  [10, 11, 15], # 8, 3
  [11, 15], # 9, 3
  [11], # 10, 3
  [12], # 1, 4
  [12, 16], # 2, 4
  [12, 13, 16], # 3, 4
  [13, 16, 17], # 4, 4
  [13, 14, 17], # 5, 4
  [14, 17, 18], # 6, 4
  [14, 15, 18], # 7, 4
  [15, 18], # 8, 4
  [15], # 9, 4
  [16], # 2, 5
  [16], # 3, 5
  [16, 17], # 4, 5
  [17], # 5, 5
  [17, 18], # 6, 5
  [18], # 7, 5
  [18], # 8, 5
]

class Node:

  # Initializer / Instance Attributes
  def __init__(self, idx):
    self.id = str(uuid.uuid4())
    self.idx = idx
    pos = nodeIdxToNodePos[idx]
    self.x = pos[0]
    self.y = pos[1]
    self.building = None
    self.roads = []
    self.connections = []

  def add_connection(self, node):
    self.connections.append(node)

  def set_building(self, building):
    self.building = building

  def add_road(self, road):
    self.roads.append(road)

  def get_free_connections(self):
    pred = lambda r: any(r.id == sr.id for sr in self.roads)
    return list(filter(lambda n: not any(pred(r) for r in n.roads), self.connections))

  def __str__(self):
    return f'x: {self.x}, y: {self.y}, id: {self.id}'