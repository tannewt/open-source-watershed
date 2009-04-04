import sys
import os
import MySQLdb as mysql

import cPickle as pickle

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = True

class Cache:
  def __init__(self):
    self.db = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
  
  def get(self, key):
    cur = self.db.cursor()
    cur.execute("SELECT value FROM cache WHERE key = %s")
    value = cur.fetchone()
    if value != None:
      value = pickle.loads(value)
      return value
    else:
      return None
  
  def cache(self, key, value, deps=[]):
    cur = self.db.cursor()
    value = pickle.dumps(value)
    cur.execute("INSERT INTO cache (key, value) VALUES (%s, %s)")
    cache_id = 2
    
    for pkg,distro in deps:
      cur.execute("INSERT INTO cache_deps (package_id, distro_id, cache_id) VALUES (%s, %s, %s)", (pkg, distro, cache_id))
  
  def evict(self, deps=[]):
    cur = self.db.cursor()
    for pkg,distro in deps:
      query = "DELETE FROM cache_deps WHERE "
      args = []
      
      if pkg == None:
        query += "package_id IS NULL AND "
      else:
        query += "package_id = %s AND "
        args.append(pkg)
      
      if distro == None:
        query += "distro_id IS NULL"
      else:
        query += "distro_id = %s"
        args.append(distro)
      
      cur.execute(query,args)
    self.db.commit()
    
    if VERBOSE:
      print cur.num_rows(),"cache lines evicted"
      
