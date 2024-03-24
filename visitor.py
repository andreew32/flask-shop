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

@bp.route('/categories', methods=('GET',))
def categories():
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  cur.execute("SELECT * FROM category")
  categories = cur.fetchall()
  return render_template('visitor/categories.html', categories=categories)

@bp.route('/category/<int:id>', methods=('GET',))
def category(id):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  cur.execute("SELECT m.id, m.title FROM feature f JOIN merch m"
              " ON f.category_id = (%s) AND f.merch_id = m.id", (id,)
  )
  prods = cur.fetchall()
  return render_template('visitor/category.html', prods=prods, catid=id)

@bp.route('/category/<int:id1>/prod/<int:id2>', methods=('GET',))
def prod(id1, id2):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  #cur.execute("SELECT * FROM merch WHERE id = (%s)", (id2,))
  cur.execute(
        "SELECT m.title, m.content, p.filename"
        " FROM merch m JOIN pic p"
        " ON m.id = p.merch_id AND m.id = (%s)", (id2,)
  )
  prod = cur.fetchall()
  prod = {'title': prod[0]['title'], 
          'content': prod[0]['content'], 
          'filenames': list(map(lambda row: row['filename'], prod))
  }
  return render_template('/visitor/prod.html', prod=prod)

@bp.route('/uploads/<name>', methods=('GET', 'POST'))
def download_pic(name):
  return send_from_directory(current_app.config['UPLOAD_FOLDER'], name)
