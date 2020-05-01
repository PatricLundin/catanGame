import os
from flask import Flask, jsonify
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
    result = db.populate_actions()
    return jsonify(result)

  # Get one action by id
  @app.route('/actions/<int:action_id>')
  def get_action_by_id(action_id):
    result = db.get_action(action_id)
    return jsonify(result)

  # Get all actions
  @app.route('/actions')
  def get_all_action():
    result = db.get_all_actions()
    return jsonify(result)

  # Test game
  @app.route('/game')
  def getGame():
    agents = [Agent() for i in range(3)]
    game = Game(agents)
    game.run_game()

    return jsonify(game.get_final_game())


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
