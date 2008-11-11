import MySQLdb as mysql
import sys
import os

sys.path.append(os.getcwd())

from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()
q = "SELECT packages.name, packages.id, packages.source_id, repos.architecture, distros.name FROM repos, distros, releases, packages WHERE repos.id=releases.repo_id AND repos.distro_id=distros.id AND releases.package_id=packages.id AND repos.branch='current' GROUP BY packages.id, repos.architecture,distros.id ORDER BY NULL"
cur.execute(q)

#print q
#print

summary = {}
for p_name,p_id,p_src,arch,dist in cur:
  if not summary.has_key(dist):
    summary[dist] = {}
  
  if not summary[dist].has_key(arch):
    summary[dist][arch] = {True:[], False:[]}
  
  p_src = p_src==None
  
  summary[dist][arch][p_src].append(p_name)

con.close()

for d in summary.keys():
  print d,"summary"
  k = summary[d].keys()
  k.sort()
  for a in k:
    if len(a)>6:
      tabs="\t"
    else:
      tabs="\t\t"
    print "\t",a,tabs,str(len(summary[d][a][True]))+"/"+str(len(summary[d][a][True])+len(summary[d][a][False]))
  print
