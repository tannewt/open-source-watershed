import sys
import os
import psycopg2 as db

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

con = db.connect(host=HOST,user=USER,password=PASSWORD,database=DB)
cur = con.cursor()
q = "SELECT dreleases.version, dreleases.revision, dreleases.released, distros.name FROM repos, distros, dreleases, packages WHERE repos.id=dreleases.repo_id AND repos.distro_id=distros.id AND dreleases.package_id=packages.id AND packages.name=%s"

args = [pkg]

if days:
  q += " AND dreleases.released > (NOW() - INTERVAL %s DAY)"
  args.append(days)

q += " ORDER BY dreleases.version ASC, dreleases.released ASC"
cur.execute(q,args)

print q%args
print

for row in cur:
  print row[2],row[0],row[1],row[3]

con.close()
