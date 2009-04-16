import sys
import os
import MySQLdb as mysql

import cPickle as pickle

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = False

# ALTER TABLE cache ADD COLUMN status TINYINT NOT NULL DEFAULT 1;

class Cache:
  STALE = -1
  REFRESH = 0
  FRESH = 1
  
  def __init__(self):
    self.db = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
  
  def has_key(self, key):
    cur = self.db.cursor()
    cur.execute("SELECT COUNT(v) FROM cache WHERE k = %s",(key,))
    self.db.commit()
    value = cur.fetchone()[0]
    if value==0:
      return False
    else:
      return True
  
  def key_status(self, key, claim=True):
    cur = self.db.cursor()
    cur.execute("SELECT status FROM cache WHERE k = %s",(key,))
    value = cur.fetchone()
    if claim and value[0] == Cache.STALE:
      cur.execute("UPDATE cache SET status = %s WHERE k = %s",(Cache.REFRESH,key))
    self.db.commit()
    if value == None:
      return None
    else:
      return value[0]
    
  def get(self, key):
    cur = self.db.cursor()
    cur.execute("SELECT v FROM cache WHERE k = %s",(key,))
    self.db.commit()
    value = cur.fetchone()[0]
    if value != None:
      value = pickle.loads(value)
      return value
    else:
      return None
  
  def put(self, key, value, deps=[]):
    cur = self.db.cursor()
    value = pickle.dumps(value)
    try:
      cur.execute("INSERT INTO cache (k, v, cached) VALUES (%s, %s, NOW())",(key,value))
      cur.execute("SELECT LAST_INSERT_ID();")
      self.db.commit()
      cache_id = cur.fetchone()[0]
    except:
      cur.execute("SELECT id FROM cache WHERE k = %s",(key,))
      cache_id = cur.fetchone()[0]
      cur.execute("UPDATE cache SET v = %s, status = %s, cached = NOW() WHERE id = %s", (value, Cache.FRESH, cache_id))
      self.db.commit()
    
    for pkg,distro in deps:
      try:
        if pkg==None or distro==None:
          if pkg==None and distro==None:
            result = cur.execute("SELECT * FROM cache_deps WHERE package_id IS NULL AND distro_id IS NULL AND cache_id = %s",(cache_id,))
          elif pkg==None and distro != None:
            result = cur.execute("SELECT * FROM cache_deps WHERE package_id IS NULL AND distro_id = %s AND cache_id = %s",(distro,cache_id))
          elif distro==None and pkg != None:
            result = cur.execute("SELECT * FROM cache_deps WHERE package_id = %s AND distro_id IS NULL AND cache_id = %s",(pkg,cache_id))
          if result>0:
            raise Exception()
        cur.execute("INSERT INTO cache_deps (package_id, distro_id, cache_id) VALUES (%s, %s, %s)", (pkg, distro, cache_id))
      except:
        pass
      self.db.commit()
  
  def evict_all(self):
    cur = self.db.cursor()
    cur.execute("DELETE FROM cache_deps")
    cur.execute("DELETE FROM cache")
    self.db.commit()
  
  def evict(self, deps=[], force=False):
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
      
      if force:
        result = cur.execute("DELETE FROM cache WHERE id IN ("+query+")",args)
      else:
        result = cur.execute("UPDATE cache SET status = %s WHERE id IN ("+query+")",[Cache.STALE]+args)
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
    
    print "cache package/distro"
    cur.execute("SELECT cache.k, packages.name, packages.id, distros.name, distros.id, cache.cached, cache.status FROM cache_deps, packages, distros, cache WHERE packages.id = cache_deps.package_id AND distros.id = cache_deps.distro_id AND cache.id = cache_deps.cache_id")
    self.db.commit()
    for row in cur:
      print row
    print
    
    print "cache package"
    cur.execute("SELECT cache.id, cache.k, packages.name, packages.id, cache.cached, cache.status FROM cache_deps, packages, cache WHERE cache_deps.distro_id IS NULL AND packages.id = cache_deps.package_id AND cache.id = cache_deps.cache_id")
    self.db.commit()
    for row in cur:
      print row
    print
    
    print "cache distro"
    cur.execute("SELECT cache.k, distros.name, distros.id, cache.cached, cache.status FROM cache_deps, distros, cache WHERE cache_deps.package_id IS NULL AND distros.id = cache_deps.distro_id AND cache.id = cache_deps.cache_id")
    self.db.commit()
    for row in cur:
      print row
    print
    
    print "cache all upstream"
    cur.execute("SELECT cache.k, cache.cached, cache.status FROM cache_deps, cache WHERE cache_deps.distro_id IS NULL AND cache_deps.package_id IS NULL AND cache.id = cache_deps.cache_id")
    self.db.commit()
    for row in cur:
      print row
    print
  
  def __del__(self):
    self.db.close()
    
if __name__=="__main__":
  c = Cache()
  if len(sys.argv)==1:
    c.put("/upstream/latest",["1", 2, 3],[(None, None)])
    c.dump()
    
    v = c.get("/upstream/latest")
    print v
    c.dump()
    
    c.evict([(None, None)])
    c.dump()
  elif sys.argv[1]=="print":
    c.dump()
  elif sys.argv[1]=="clear":
    c.evict_all()
  elif len(sys.argv)==4 and sys.argv[1]=="evict":
    pkg = eval(sys.argv[2])
    distro = eval(sys.argv[3])
    c.evict([(pkg, distro)])
  else:
    print sys.argv[0],"unknown command"
