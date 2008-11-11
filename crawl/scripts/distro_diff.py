import MySQLdb as mysql
import sys
import os

sys.path.append(os.getcwd())

if len(sys.argv)<7:
  print sys.argv[0],"<name> <branch> <architecture> <name> <branch> <architecure>"
  sys.exit(-1)
else:
  name1, branch1, arch1 = sys.argv[1:4]
  name2, branch2, arch2 = sys.argv[4:]

from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()
q = "SELECT DISTINCT packages.name FROM repos, distros, releases, packages WHERE repos.id=releases.repo_id AND repos.distro_id=distros.id AND releases.package_id=packages.id AND packages.source_id IS NULL AND distros.name=%s AND repos.branch=%s AND repos.architecture=%s"
cur.execute(q,(name1,branch1,arch1))
set1 = set()
for p in cur:
  set1.add(p[0])

cur.execute(q,(name2,branch2,arch2))
set2 = set()
for p in cur:
  set2.add(p[0])
con.close()

print len(set1-set2),len(set1 & set2),len(set2 - set1)

cruft = {}
for p in set1 ^ set2:
  if p in set1:
    cruft[p] = name1
  else:
    cruft[p] = name2

keys = cruft.keys()
keys.sort()
for k in keys[-100:]:
  print k,cruft[k]
