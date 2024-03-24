import functools
import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import current_app

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/addcategory', methods=('GET', 'POST'))
def addcategory():
  if request.method == 'POST':
    title = request.form['title']
    cur = get_db().cursor()
    error = None

    if not title:
      error = 'name is required'

    if error is None:
      try:
        cur.execute("INSERT INTO category (title) VALUES (%s)", (title,))
        get_db().commit()
      except Exception as e: #db.IntegrityError:
        error = str(e)
      else:
        return redirect(url_for("admin.addcategory"))
    flash(error)
  return render_template('admin/addcategory.html')

@bp.route('/addmerch', methods=('GET', 'POST'))
def addmerch():
  categories = []
  if request.method == 'POST':
    title = request.form['title']
#    content = request.form['content']
    content = ""
    category_id = None
    if request.form['category_id'] != "None":
      category_id = request.form['category_id']
    cur = get_db().cursor()
    error = None
    
    if not title:
      error = 'name is required'
    
    if error is None:
      try:
        cur.execute(
            "INSERT INTO merch (title, content) VALUES (%s, %s) RETURNING id", 
            (title, content)
        )
        if category_id:
          merch_id = cur.fetchone()
          cur.execute(
              "INSERT INTO feature (merch_id, category_id) VALUES (%s, %s)",
              (merch_id, category_id)
          )
        get_db().commit()
      except Exception as e:#db.IntegrityError:
        error = str(e)
      else:
        return redirect(url_for("admin.addmerch"))
    flash(error)
  else:
    cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()
    #categories = map(lambda row: dict(row), categories)
  return render_template('admin/addmerch.html', categories=categories)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
            current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/addpic/category/<int:id1>/prod/<int:id2>', methods=('GET', 'POST'))
def addpic(id1, id2):
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(os.getcwd(), current_app.config['UPLOAD_FOLDER'], 
                              filename))
      cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
      cur.execute("SELECT id FROM merch WHERE id = (%s)", (id2,))
      if cur.fetchone():
        cur.execute(
                "INSERT INTO pic (merch_id, filename) VALUES (%s, %s)",
                (id2, filename)
            )
        get_db().commit()
  return '''
  <!doctype html>
  <title>Upload new File</title>
  <h1>Upload new File</h1>
  <form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input type=submit value=Upload>
  </form>
  '''

