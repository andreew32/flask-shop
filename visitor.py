import functools
import psycopg2
import psycopg2.extras
from flask import current_app
from flask import send_from_directory

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import get_db

bp = Blueprint('visitor', __name__, url_prefix='/visitor')

def getcatssets():
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("SELECT * FROM category")
  cats = cur.fetchall()
  cur.execute("SELECT * FROM set")
  sets = cur.fetchall()
  catssets = {}
  def getcats(set_id):
    x = {}
    for cat in cats:
      if cat['set_id'] == set_id:
        x[cat['title']] = cat['id']
    return x
  for set in sets:
    id = set['id']
    catssets[set['title']] = {'id': id, 'categories': getcats(id)}
  cur.close()
  return catssets

def render_template_nav(template, **context):
  return render_template(template, sets=getcatssets(), **context)

@bp.route('/categories', methods=('GET',))
def categories():
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  cur.execute("SELECT * FROM category")
  categories = cur.fetchall()
  return render_template_nav('visitor/categories.html', categories=categories)

@bp.route('/category/<int:id>', methods=('GET',))
def category(id):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  cur.execute("SELECT m.id, m.title FROM feature f JOIN merch m"
              " ON f.category_id = (%s) AND f.merch_id = m.id", (id,)
  )
  prods = cur.fetchall()
  return render_template_nav('visitor/category.html', prods=prods, catid=id)

@bp.route('/category/<int:id1>/prod/<int:id2>', methods=('GET',))
def prod(id1, id2):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  error = None
  cur.execute("SELECT m.title, m.content FROM merch m WHERE m.id = (%s)", (id2,))
  prod = cur.fetchone()
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("SELECT p.filename FROM pic p WHERE p.merch_id = (%s)", (id2,))
  filenames = cur.fetchall()
  prod['filenames'] = list(map(lambda row: row[0], filenames))
  return render_template_nav('/visitor/prod.html', prod=prod)

@bp.route('/set/<int:id>', methods=('GET',))
def set(id):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  cur.execute("SELECT merch.id, merch.title FROM category "
              "JOIN set ON category.set_id = set.id AND category.set_id = (%s) "
              "JOIN feature ON feature.category_id = category.id "
              "JOIN merch ON feature.category_id = category.id AND feature.merch_id = merch.id;", 
              (id,)
  )
  prods = cur.fetchall()
  return render_template_nav('visitor/set.html', prods=prods, setid=id)

@bp.route('/uploads/<name>', methods=('GET', 'POST'))
def download_pic(name):
  return send_from_directory(current_app.config['UPLOAD_FOLDER'], name)

