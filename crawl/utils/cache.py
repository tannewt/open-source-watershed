import sys
import os
import MySQLdb as mysql

import cPickle as pickle

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = False

class Cache:
  def __init__(self):
    self.db = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
  
  def has_key(self, key):
    cur = self.db.cursor()
    cur.execute("SELECT COUNT(v) FROM cache WHERE k = %s",(key,))
    value = cur.fetchone()[0]
    if value == 0:
      return False
    else:
      return True
    
  def get(self, key):
    cur = self.db.cursor()
    cur.execute("SELECT v FROM cache WHERE k = %s",(key,))
    value = cur.fetchone()[0]
    if value != None:
      value = pickle.loads(value)
      return value
    else:
      return None
  
  def put(self, key, value, deps=[]):
    cur = self.db.cursor()
    value = pickle.dumps(value)
    cur.execute("INSERT INTO cache (k, v, cached) VALUES (%s, %s, NOW())",(key,value))
    cur.execute("SELECT LAST_INSERT_ID();")
    cache_id = cur.fetchone()[0]
    
    for pkg,distro in deps:
      cur.execute("INSERT INTO cache_deps (package_id, distro_id, cache_id) VALUES (%s, %s, %s)", (pkg, distro, cache_id))
      self.db.commit()
  
  def evict(self, deps=[]):
    cur = self.db.cursor()
    rows = 0
    for pkg,distro in deps:
      query = "SELECT cache_id FROM cache_deps WHERE "
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
      
      result = cur.execute("DELETE FROM cache WHERE id IN ("+query+")",args)
      rows += result
      self.db.commit()
    
    if VERBOSE:
      print rows,"cache line(s) evicted"
  
  def dump(self):
    cur = self.db.cursor()
    
    #print "cache"
    #cur.execute("SELECT * FROM cache")
    #for row in cur:
    #  print row
    #print
    
    print "cache deps"
    cur.execute("SELECT packages.name, distros.id, cache.caches FROM cache_deps, packages, distros, cache WHERE packages.id = cache_deps.package_id AND distros.id = cache_deps.distro_id AND cache.id = cache_deps.cache_id")
    for row in cur:
      print row
    print
  
  def __del__(self):
    self.db.close()
    
if __name__=="__main__":
  c = Cache()
  if len(sys.argv)>1 and sys.argv[1]=="print":
    c.dump()
  else:
    c.put("/upstream/latest",["1", 2, 3],[(None, None)])
    c.dump()
    
    v = c.get("/upstream/latest")
    print v
    c.dump()
    
    c.evict([(None, None)])
    c.dump()
