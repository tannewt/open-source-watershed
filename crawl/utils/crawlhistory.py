import sys
import os
import MySQLdb as mysql
import datetime

sys.path.append(os.getcwd())
from utils import helper
from utils import cache

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class CrawlHistory:
  def __init__(self,package=None,distro=None):
    c = cache.Cache()
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
      if c.has_key(key):
        self.releases = c.get(key)
        cached = True
      else:
        cur.execute("SELECT packages.name, releases.version, releases.released FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL GROUP BY releases.package_id, releases.version ORDER BY releases.released DESC LIMIT 25")
    elif package == None and distro != None:
      key = "/distro/%s/latest"%distro
      if c.has_key(key):
        self.releases = c.get(key)
        cached = True
      else:
        cur.execute("SELECT packages.name, releases.version, releases.revision, releases.released FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s GROUP BY releases.package_id, releases.version ORDER BY releases.released DESC LIMIT 25",(distro,))
    elif package != None and distro == None:
      key = "/pkg/%s/latest"%package
      if c.has_key(key):
        self.releases = c.get(key)
        cached = True
      else:
        cur.execute("SELECT packages.name, releases.version, releases.released FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL AND packages.name = %s GROUP BY  releases.version ORDER BY releases.released DESC LIMIT 25",(package,))
    else:
      key = "/distro/%s/pkg/%s/latest"%(distro,package)
      if c.has_key(key):
        self.releases = c.get(key)
        cached = True
      else:
        cur.execute("SELECT packages.name, releases.version, releases.revision, releases.released FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s AND packages.name = %s GROUP BY releases.package_id, releases.version, releases.revision ORDER BY MIN(releases.released) DESC LIMIT 25",(distro,package))
    
    self.today = 0
    now = datetime.datetime.now()
    day = datetime.timedelta(1)
    if cached:
      for row in self.releases:
        if now-row[-1] <= day:
          self.today += 1
    else:
      for row in cur:
        self.releases.append(row)
        if now-row[-1] <= day:
          self.today += 1
      print "cache!"
      c.put(key,self.releases,[(package_id,distro_id)])
  
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
