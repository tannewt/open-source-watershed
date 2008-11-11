import MySQLdb as mysql
import sys
import os

sys.path.append(os.getcwd())

from utils import helper


if len(sys.argv)>1:
  pkg = sys.argv[1]
  days = None
elif len(sys.argv)>2:
  pkg = sys.argv[1]
  days = sys.argv[2]
else:
  print sys.argv[0],"<package> [<days>]"
  sys.exit(-1)


HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()
q = "SELECT releases.version, releases.revision, releases.released, distros.name FROM repos, distros, releases, packages WHERE repos.id=releases.repo_id AND repos.distro_id=distros.id AND releases.package_id=packages.id AND packages.name=%s"

args = [pkg]

if days:
  q += " AND releases.released > (NOW() - INTERVAL %s DAY)"
  args.append(days)

q += " ORDER BY releases.version ASC, releases.released ASC"
cur.execute(q,args)

print q%args
print

for row in cur:
  print row[2],row[0],row[1],row[3]

con.close()
