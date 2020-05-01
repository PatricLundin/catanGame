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

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

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