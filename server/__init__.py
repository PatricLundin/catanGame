import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from json import JSONEncoder
from flask_socketio import SocketIO, emit
from . import db
import json

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default

def create_app(test_config=None):
  from game.game import Game
  from game.agent import Agent
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  CORS(app)
  app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
  )
  if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
  else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

  # ensure the instance folder exists
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  socketio = SocketIO(app, cors_allowed_origins="*")

  if __name__ == '__main__':
    socketio.run(app)

  db.init_app(app)

  # Test init db
  @app.route('/init_db')
  def initDB():
    actions = db.populate_actions()
    players = db.populate_base_players()
    return jsonify(players + actions)

  # Take one action
  @app.route('/take_action')
  def take_action():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    action_id = request.args.get('action_id')
    db.take_action(game_id=game_id, player_id=player_id, action_id=action_id)
    return jsonify(db.get_game(game_id))

  # Next turn
  @app.route('/next_turn')
  def next_turn():
    game_id = request.args.get('game_id')
    db.next_turn(game_id=game_id)
    return jsonify(db.get_game(game_id))

  # Get one action by id
  @app.route('/actions/<int:action_id>')
  def get_action_by_id(action_id):
    result = db.get_action(action_id)
    return jsonify(result)

  # Get one action by id
  @app.route('/create_player')
  def create_player():
    username = request.args.get('username')
    color = request.args.get('color')
    result = db.create_player(username, color)
    return jsonify(result)

  # Get all actions
  @app.route('/actions')
  def get_all_action():
    result = db.get_all_actions()
    return jsonify(result)

  # Create new game
  @app.route('/game')
  def create_game():
    players = [int(p) for p in request.args.getlist('players')]
    print(players)
    try:
      game = db.create_game(players)
    except ValueError as error:
      print(error)
      return jsonify({ 'Error': str(error) })
    print(game)
    return jsonify(game)


  # Socket.io

  @socketio.on('get_all_actions')
  def socket_actions():
    result = db.get_all_actions()
    emit('all_actions', result)

  @socketio.on('new_game')
  def new_game():
    agents = [Agent() for i in range(3)]
    game = Game(agents)
    game.run_game()
    emit('game_response', game.get_final_game())

  return app
