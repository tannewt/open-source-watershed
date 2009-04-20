import sys
import os
import MySQLdb as mysql
import datetime
import threading

sys.path.append(os.getcwd())
from utils import helper
from utils.cache import Cache

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class CrawlHistory:
  def __init__(self,package=None,distro=None):
    c = Cache()
    self.releases = []
    
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    if package != None:
      cur.execute("SELECT id FROM packages WHERE name = %s",(package,))
      package_id = cur.fetchone()[0]
    else:
      package_id = None
    
    if distro != None:
      cur.execute("SELECT id FROM distros WHERE name = %s",(distro,))
      distro_id = cur.fetchone()[0]
    else:
      distro_id = None
    
    cached = False
    if package == None and distro == None:
      key = "/upstream/latest"
      query = "SELECT packages.name, releases.version, MIN(releases.released) FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL AND releases.released >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY releases.package_id, releases.version ORDER BY MIN(releases.released) DESC"
      query_args = []
    elif package == None and distro != None:
      key = "/distro/%s/latest"%distro
      query = "SELECT packages.name, releases.version, releases.revision, MIN(releases.released) FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s AND releases.released >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY packages.id, releases.version ORDER BY MIN(releases.released) DESC"
      query_args = (distro,)
    elif package != None and distro == None:
      key = "/pkg/%s/latest"%package
      query = "SELECT packages.name, releases.version, MIN(releases.released) FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL AND packages.name = %s GROUP BY  releases.version ORDER BY MIN(releases.released) DESC"
      query_args = (package,)
    else:
      key = "/distro/%s/pkg/%s/latest"%(distro,package)
      query = "SELECT packages.name, releases.version, releases.revision, MIN(releases.released) FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s AND packages.name = %s GROUP BY releases.package_id, releases.version, releases.revision ORDER BY MIN(releases.released) DESC"
      query_args = (distro,package)
    
    now = datetime.datetime.now()
    day = datetime.timedelta(1)
    
    status = c.key_status(key)
    if status != None:
      self.releases = c.get(key)
      if status == Cache.STALE:
        t = threading.Thread(target=self.update, args=(key, query, query_args, package_id, distro_id))
        t.start()
    else:
      self.update(key, query, query_args, package_id, distro_id)
      
    self.today = len(self.releases)
  
  def update(self, key, query, query_args, package_id, distro_id, cache=None):
    if cache == None:
      cache = Cache()
    
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    cur.execute(query, query_args)
    
    tmp = []
    for row in cur:
      tmp.append(row)
    
    self.releases = tmp
    
    cache.put(key,tmp,[(package_id,distro_id)])
  
  def __str__(self):
    result = []
    for rel in self.releases:
      result.append(" ".join(map(str,rel)))
    return "\n".join(result)

if __name__=="__main__":
  print CrawlHistory()
  print
  print CrawlHistory("gcc")
  print
  print CrawlHistory(None,"ubuntu")
  print
  print CrawlHistory("inkscape","ubuntu")
