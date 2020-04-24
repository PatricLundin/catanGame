import os
from flask import Flask, jsonify

def create_app(test_config=None):
  from game.game import Game
  from game.agent import Agent
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
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

  # a simple page that says hello
  @app.route('/hello')
  def hello():
    return 'Hello, World!'

  # Test game
  @app.route('/game')
  def getGame():
    agents = [Agent() for i in range(3)]
    game = Game(agents)
    game.run_game()
    return jsonify(game.get_state(game.players[0]))

  return app