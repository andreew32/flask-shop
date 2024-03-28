import psycopg2

import click

from flask import current_app, g

from . import init_db

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host="localhost",
            database="shopa_db",
            user="flask",
            password="flask"
        )
        #g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@click.command('init-db')
def init_db_command():
  init_db.init_db()
  click.echo('Initialized the database')

@click.command('init-test-db')
def init_test_db_command():
  init_db.init_test_db()
  click.echo('Initialized the test database')

@click.command('fill-db')
def fill_db_command():
  init_db.fill_db("shopa_db")
  click.echo("Filled the database")

@click.command('fill2-db')
def fill2_db_command():
  init_db.fill2_db("shopa_db")
  click.echo("Filled by 2 the database")

@click.command('fill3-db')
def fill3_db_command():
  init_db.fill3_db("shopa_db")
  click.echo("Filled by 3 the database")

@click.command('fillall-db')
def fillall_db_command():
  db = 'shopa_db'
  init_db.fill_db(db)
  init_db.fill2_db(db)
  init_db.fill3_db(db)
  #init_db.fill4_db(db)
  click.echo("Filled all the database")

def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
  app.cli.add_command(init_test_db_command)
  app.cli.add_command(fill_db_command)
  app.cli.add_command(fill2_db_command)
  app.cli.add_command(fill3_db_command)
  app.cli.add_command(fillall_db_command)
