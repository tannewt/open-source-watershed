import sys
import os
import MySQLdb as mysql

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class CrawlHistory:
  def __init__(self,package=None,distro=None):
    self.releases = []
    
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    if package == None and distro == None:
      cur.execute("SELECT packages.name, releases.version, releases.released FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL GROUP BY releases.package_id, releases.version ORDER BY releases.released DESC LIMIT 25")
    elif package == None and distro != None:
      cur.execute("SELECT packages.name, releases.version, releases.revision, releases.released FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s GROUP BY releases.package_id, releases.version ORDER BY releases.released DESC LIMIT 25",(distro,))
    elif package != None and distro == None:
      cur.execute("SELECT packages.name, releases.version, releases.released FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL AND packages.name = %s GROUP BY  releases.version ORDER BY releases.released DESC LIMIT 25",(package,))
    else:
      cur.execute("SELECT packages.name, releases.version, releases.revision, releases.released FROM packages, releases, repos, distros WHERE packages.id = releases.package_id AND repos.id = releases.repo_id AND distros.id = repos.distro_id AND distros.name = %s AND packages.name = %s GROUP BY releases.package_id, releases.version, releases.revision ORDER BY MIN(releases.released) DESC LIMIT 25",(distro,package))
    for row in cur:
      self.releases.append(row)
  
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
