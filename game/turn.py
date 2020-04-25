import json

class Turn:
  def __init__(self, index, player, moves, dice_roll):
    self.index = index
    self.player = player
    self.moves = moves
    self.dice_roll = dice_roll

  def move_to_string(self, move):
    _, action, _, _, _, turn = move
    return (turn, self.player.actionId_to_action(action))

  def to_json(self):
    return {
      'i': self.index,
      'player': self.player.name,
      'moves': [self.move_to_string(m) for m in self.moves],
      'dice_roll': self.dice_roll
    }

  def __str__(self):
    return f'i: {self.index}, player: {self.player.name}, moves: {str([self.move_to_string(m) for m in self.moves])}'
