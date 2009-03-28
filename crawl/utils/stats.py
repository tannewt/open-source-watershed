import sys
import os
import MySQLdb as mysql

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class DataStats:
  def __init__(self):
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM distros;")
    self.distro_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM packages;")
    self.package_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT( DISTINCT package_id ) FROM releases WHERE repo_id IS NULL;")
    self.upstream_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(DISTINCT package_id, version, revision, repos.codename) FROM releases, repos WHERE releases.repo_id = repos.id;");
    self.release_count = cur.fetchone()[0]
    con.close()
  
  def __str__(self):
    result = []
    result.append("Total distros: "+str(self.distro_count))
    result.append("Total packages: "+str(self.package_count))
    result.append("Upstream Packages: "+str(self.upstream_count))
    result.append("Total releases: "+str(self.release_count))
    return "\n".join(result)

if __name__=="__main__":
  s = DataStats()
  print s
