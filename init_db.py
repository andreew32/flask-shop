#import os
import psycopg2

def connect(dbname):
  return psycopg2.connect(
          host="localhost",
          database=dbname,
          user='flask',
          password='flask'
  )

def drop_create_db(conn):
  cur = conn.cursor()
  cur.execute('DROP TABLE IF EXISTS feature;')
  cur.execute('DROP TABLE IF EXISTS category;')
  cur.execute('DROP TABLE IF EXISTS pic;')
  cur.execute('DROP TABLE IF EXISTS merch;')
  cur.execute('CREATE TABLE merch (id serial PRIMARY KEY,'
                                  'title varchar (150),'
                                  'content TEXT);'
                                  )
  cur.execute('CREATE TABLE category (id serial PRIMARY KEY,'
                                      'title varchar (255));')
  cur.execute('CREATE TABLE feature (id serial PRIMARY KEY,'
                                    'merch_id INTEGER,'
                                    'category_id INTEGER,'
                                    'FOREIGN KEY (merch_id) REFERENCES merch (id),'
                                    'FOREIGN KEY (category_id) REFERENCES category (id));'
                                    )
  cur.execute('CREATE TABLE pic (id serial PRIMARY KEY,'
                                  'merch_id INTEGER,'
                                  'filename VARCHAR (255),'
                                  'FOREIGN KEY (merch_id) REFERENCES merch (id));')
  conn.commit()
  cur.close()

def init_db():
  conn = psycopg2.connect(
          host="localhost",
          database="shopa_db",
          user='flask', #os.environ['DB_USERNAME'],
          password='flask' #os.environ['DB_PASSWORD']
  )
  drop_create_db(conn)
  conn.close()

def init_test_db():
  conn = psycopg2.connect(
          host="localhost",
          database="shoptest_db",
          user="flask",
          password="flask"
  )
  drop_create_db(conn)
  fill_db("shoptest_db")
  conn.close()

def fill_db(database):
  conn = psycopg2.connect(
          host="localhost",
          database=database,
          user="flask",
          password="flask"
  )
  cur = conn.cursor()
  categories = {
    "fruits & vegs": 1,
    "bread": 1,
    "dairy": 1
  }
  for catname in categories:
    cur.execute("INSERT INTO category (title) VALUES (%s) RETURNING id;", (catname,))
    categories[catname] = cur.fetchone()
  merches = {
    "tomus borodin": {'catid': categories["bread"], 'id': 1},
    "tomus suit": {'catid': categories["bread"], 'id': 1},
    "tomus rozh": {'catid': categories["bread"], 'id': 1},
    "kefir gonezlik": {'catid': categories["dairy"], 'id': 1},
    "kefir elin": {'catid': categories["dairy"], 'id': 1},
    "kefir yazlyk": {'catid': categories["dairy"], 'id': 1},
    "banana": {'catid': categories["fruits & vegs"], 'id': 1},
    "turkey pear": {'catid': categories["fruits & vegs"], 'id': 1},
    "pear at place": {'catid': categories["fruits & vegs"], 'id': 1},
  }
  for merchname in merches:
    cur.execute("INSERT INTO merch (title) VALUES (%s) RETURNING id;", (merchname,))
    merches[merchname]['id'] = cur.fetchone()
    cur.execute("INSERT INTO feature (merch_id, category_id) VALUES (%s, %s);",
                (merches[merchname]['id'], merches[merchname]['catid'])
    )
  conn.commit()
  cur.close()
  conn.close()

def fill2_db(database):
  conn = psycopg2.connect(
          host="localhost",
          database=database,
          user="flask",
          password="flask"
  )
  cur = conn.cursor()
  cur.execute("INSERT INTO category (title) VALUES ('confectionary') RETURNING id;")
  catid = cur.fetchone()
  for i in range(1,100):
    cur.execute("INSERT INTO merch (title) VALUES (%s) RETURNING id;", ('confectionary'+str(i),))
    id = cur.fetchone()
    cur.execute("INSERT INTO feature (merch_id, category_id) VALUES (%s, %s);", (id,catid))
  conn.commit()
  cur.close()
  conn.close()

def fill3_db(database):
  conn = connect(database)
  cur = conn.cursor()
  cur.execute(
        "INSERT INTO pic (merch_id, filename)"
        "VALUES (3, 'fuck you motherfucker')"
  )
  cur.execute(
        "INSERT INTO pic (merch_id, filename)"
        "VALUES (3, 'you bitch')"
  )
  cur.execute(
        "INSERT INTO pic (merch_id, filename)"
        "VALUES (3, 'Screenshot_from_2023-07-13_23-02-56.png')"
  )
  cur.execute(
        "INSERT INTO pic (merch_id, filename)"
        "VALUES (3, 'Screenshot_from_2023-07-13_23-04-42.png')"
  )
  conn.commit()
  cur.close()
  conn.close()

#def fill4_db(database):
#  conn = connect(database)
#  cur = conn.cursor()
#  cur.execute(
#        "INSERT INTO pic (merch_id, filename)"
#        "VALUES (3, 'fuck you motherfucker')"
#  )
#  cur.execute(
#        "INSERT INTO pic (merch_id, filename)"
#        "VALUES (3, 'you bitch')"
#  )
#  conn.commit()
#  cur.close()
#  conn.close()

