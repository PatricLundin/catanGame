import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import numpy as np
from game.enums import Actions, GRID_TYPES
import collections

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    populate_actions()
    populate_base_players()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# Game
def create_game(players):
  if len(players) < 2 or len(players) > 4:
    raise ValueError('A game requires two to four players')
  db = get_db()
  try:
    players = get_players_by_ids(players)
  except ValueError:
    raise

  game_cursor = db.execute('INSERT INTO game (current_player) VALUES (?)', (players[0]['id'], ))
  for player in players:
    db.execute('INSERT INTO game_players (game_id, player_id) VALUES (?, ?)', (game_cursor.lastrowid, player['id']))

  db.commit()
  return get_game(game_cursor.lastrowid)

def get_game(game_id):
  db = get_db()

  game_from_db = db.execute('SELECT * FROM game WHERE id=?', (game_id, )).fetchone()

  players_list = players_in_game(game_id)

  game_turns = db.execute('''
  SELECT t.turn_index, ta.player_id, ta.action_id
  FROM turn as t
  INNER JOIN turn_action as ta
  ON t.id=ta.turn_id
  WHERE t.game_id={}
  ORDER BY t.turn_index
  '''.format(game_id)).fetchall()
  turn_list = []
  for row in game_turns:
    d = {}
    for key in row.keys():
      d[key] = row[key]
    turn_list.append(d)

  if len(turn_list) > 0:
    turns = []
    for _ in [None] * (turn_list[len(turn_list) - 1]['turn_index'] + 1):
      turns.append([])
    for turn in turn_list:
      turns[turn['turn_index']].append({ 'player_id': turn['player_id'], 'action_id': turn['action_id'] })
  else:
    turns = []

  game = {
    'id': game_from_db['id'],
    'current_turn': game_from_db['current_turn'],
    'current_player': game_from_db['current_player'],
    'players': players_list,
    'turns': turns,
  }

  return game

def game_finished(game_id):
  db = get_db()
  db.execute('UPDATE game SET completed = 1 WHERE id=?', (game_id, ))
  db.commit()

# players
def create_player(username, color):
  db = get_db()
  try:
    cursor = db.execute('INSERT INTO player (username, color) VALUES (?, ?)', (username, color))
    db.commit()
    row = db.execute('SELECT * FROM player WHERE id=?', (cursor.lastrowid,)).fetchone()
    d = collections.OrderedDict()
    for key in row.keys():
        d[key] = row[key]
    return d
  except sqlite3.IntegrityError as err:
    print(err)
    return
  
def get_players_by_ids(player_ids):
  db = get_db()
  rows = db.execute('SELECT * FROM player WHERE id in {}'.format(tuple(player_ids))).fetchall()
  if not len(rows) == len(player_ids):
    raise ValueError('All players not found in database')
  objects_list = []
  for row in rows:
      d = {}
      for key in row.keys():
          d[key] = row[key]
      objects_list.append(d)
  sorted_players = []
  for player in player_ids:
    for p in objects_list:
      if int(p['id']) == player:
        sorted_players.append(p)
  return sorted_players

def get_all_players():
  db = get_db()
  rows = db.execute('SELECT * FROM player').fetchall()
  objects_list = []
  for row in rows:
      d = collections.OrderedDict()
      for key in row.keys():
          d[key] = row[key]
      objects_list.append(d)
  return objects_list

def populate_base_players():
  db = get_db()
  db.execute('DELETE FROM player')
  players = [('RED', '0xc94524'), ('BLUE', '0x2469c9'), ('PINK', '0xf092f0'), ('BLACK', '0x242120')]
  db.executemany('INSERT INTO player (username, color) VALUES (?,?)', players)
  db.commit()
  return get_all_players()

def players_in_game(game_id):
  db = get_db()
  game_players = db.execute('''
  SELECT p.id, p.username as name, p.color
  FROM player as p
  INNER JOIN game_players as gp
  ON p.id=gp.player_id
  WHERE gp.game_id={}
  '''.format(game_id)).fetchall()
  players_list = []
  for row in game_players:
    d = {}
    for key in row.keys():
      d[key] = row[key]
    players_list.append(d)
  return players_list

# Turns 
def next_turn(game_id):
  db = get_db()
  players = players_in_game(game_id)
  game_from_db = db.execute('SELECT * FROM game WHERE id=?', (game_id, )).fetchone()
  for idx, player in enumerate(players):
    if int(game_from_db['current_player']) == int(player['id']):
      next_player = players[(idx + 1) % len(players)]['id']
  db.execute('UPDATE game SET current_turn = current_turn + 1, current_player = ? WHERE id=?', (next_player, game_id))
  db.commit()

def set_dice_trow(game_id, dice_one, dice_two):
  db = get_db()
  game = get_game(game_id)
  db.execute('UPDATE turn SET dice_one = ?, dice_two = ? WHERE game_id=? AND turn_index=?', (dice_one, dice_two, game_id, int(game['current_turn'])))
  db.commit()

# Actions
def take_action(game_id, player_id, action_id):
  db = get_db()
  game = get_game(game_id)

  # Find current turn and insert if new current turn
  if not game['current_turn'] == len(game['turns']) - 1:
    turn_cursor = db.execute('INSERT INTO turn (game_id, turn_index) VALUES (?,?)', (game_id, game['current_turn']))
    turn_id = turn_cursor.lastrowid
  else:
    turn_row = db.execute('SELECT * FROM turn WHERE game_id=? AND turn_index=?', (game_id, game['current_turn'])).fetchone()
    turn_id = turn_row['id']

  # Insert turn action
  db.execute('''
    INSERT INTO turn_action (turn_id, action_id, player_id)
    VALUES (?,?,?)
  ''', (turn_id, action_id, player_id))

  db.commit()

def get_action(id):
    db = get_db()
    row = db.execute('SELECT * FROM actions WHERE id=?', (id,)).fetchone()
    d = collections.OrderedDict()
    for key in row.keys():
        d[key] = row[key]
    return d

def get_all_actions():
    db = get_db()
    rows = db.execute('SELECT * FROM actions').fetchall()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        for key in row.keys():
            d[key] = row[key]
        objects_list.append(d)
    return objects_list

def populate_actions():
    db = get_db()
    db.execute('DELETE FROM actions')
    
    nodes = np.arange(54)
    roads = np.arange(72)
    resources = [GRID_TYPES.WHEAT, GRID_TYPES.STONE, GRID_TYPES.BRICKS, GRID_TYPES.WOOD, GRID_TYPES.SHEEP]

    no_action = [[Actions.NOACTION, 0, None]]
    village_actions = [[Actions.BUILDING, idx, None]for idx, n in enumerate(nodes)]
    city_actions = [[Actions.UPGRADE, idx, None]for idx, n in enumerate(nodes)]
    road_actions = [[Actions.ROAD, idx, None]for idx, r in enumerate(roads)]
    trade_actions = []
    for r1 in resources:
      for r2 in resources:
        if not r1 == r2:
          trade_actions.append([Actions.TRADE, r1.value, r2.value])
    all_actions = no_action + village_actions + city_actions + road_actions + trade_actions
    for idx, action in enumerate(all_actions):
      if not action is None:
        action.insert(0, idx)
    db.executemany('INSERT INTO actions VALUES (?,?,?,?)', all_actions)
    db.commit()
    return get_all_actions()