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

def getnavcategories():
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("SELECT * FROM category")
  cats = cur.fetchall()
  cur.execute("SELECT * FROM set")
  sets = cur.fetchall()
  navpanel = {}
  def getcategories(set_id):
    x = {}
    for cat in cats:
      if cat['set_id'] == set_id:
        x[cat['title']] = cat['id']
    return x
  for set in sets:
    id = set['id']
    navpanel[set['title']] = {'id': id, 'categories': getcategories(id)}
  cur.close()
  return navpanel

def addimages(prods):
  #top = 5
#  prods = {}
#  if smallgrid:
#    cur.execute("SELECT TOP 5 merch.title, merch.content, merch.id FROM merch ")
#  if category:
#    cur.execute("SELECT merch.title, merch.content, merch.id FROM merch "
#                "JOIN feature ON feature.merch_id = merch.id "
#                "WHERE feature.category_id = (%s)", (category,)
#    )
#    prods = cur.fetchall()
#  if set:
#    cur.execute("SELECT merch.title, merch.content, merch.id FROM merch "
#                "JOIN feature ON feature.merch_id = merch.id "
#                "JOIN category ON feature.category_id = category.id "
#                "JOIN set ON category.set_id = set.id "
#                "WHERE set.id = (%s)", (set,)
#    )
#    prods = cur.fetchall()
  prod_ids = "'" + str(prods[0]['id']) + "'" #to get all images in one request
  for i in range(len(prods)):
    prod_ids += ",'" + str(prods[i]['id']) + "'"
  cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  cur.execute("SELECT * FROM pic WHERE pic.merch_id IN (" + prod_ids + ")")
  pics = cur.fetchall()
  cur.close()
  prod_list = [] #to arrange pics from the mess among the products
  def addpics(prod):
    new_prod = {}
    for key in prod: #make normal dictionary from a <psycopg2 unchangable object>
      new_prod[key] = prod[key]
    new_prod['pics'] = []
    for i in range(len(pics)):
      if pics[i]['merch_id'] == new_prod['id']:
        new_prod['pics'] += [pics[i]['filename']]
    #print(new_prod)
    return new_prod
  for i in range(len(prods)):
    prod_list += [addpics(prods[i])]
  #print(prod_list)
#  new_list = [] #pack all the products into bunches of 5 products each
#  i = 0 
#  while i < len(prods):
#    z = i + 5
#    new_list += [prod_list[i:z]]
#    i = z
  return prod_list
  
def render_template_nav(template, **context):
  return render_template(template, sets=getnavcategories(), **context)

@bp.route('/categories', methods=('GET',))
def categories():
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  error = None
  cur.execute("SELECT * FROM category")
  categories = cur.fetchall()
  return render_template_nav('visitor/categories.html', categories=categories)

@bp.route('/category/<int:id>', methods=('GET',))
def category(id):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  error = None
  cur.execute("SELECT m.id, m.title FROM feature f JOIN merch m"
              " ON f.category_id = (%s) AND f.merch_id = m.id", (id,)
  )
  prods = cur.fetchall()
  prods = addimages(prods)
  return render_template_nav('visitor/category.html', prods=prods, catid=id)

@bp.route('/prod/<int:id>', methods=('GET',))
def prod(id):
  cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  error = None
  cur.execute("SELECT m.title, m.content FROM merch m WHERE m.id = (%s)", (id,))
  prod = cur.fetchone()
  cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("SELECT p.filename FROM pic p WHERE p.merch_id = (%s)", (id,))
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

