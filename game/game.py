from game.board import Board
from game.node import Node, nodeToHex
from game.road import connectionIdxToNodeIdx

class Game:

    # Initializer / Instance Attributes
  def __init__(self, agents):
    self.agents = agents
    self.board = Board.generate_random_board()
    self.nodes = self.init_nodes()
    print('Game initiated')

  def init_nodes(self):
    nodes = [Node(i) for i in range(54)]
    for idx, node in enumerate(nodes):
      boardPositions = nodeToHex[idx]
      for boardIdx in boardPositions:
        self.board[boardIdx].add_node(node)

    for conn in connectionIdxToNodeIdx:
      nodes[conn[0]].add_connection(nodes[conn[1]])
      nodes[conn[1]].add_connection(nodes[conn[0]])
    return nodes
