import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())

if len(sys.argv)<2:
  print sys.argv[0],"<architecture>"
  sys.exit(-1)
else:
  arch = sys.argv[1]

from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()

q = "SELECT distros.name, repos.branch, YEAR(crawls.time), MONTH(crawls.time), DAY(crawls.time), SUM(crawls.release_count) FROM repos, distros, crawls WHERE repos.id=crawls.repo_id AND repos.distro_id=distros.id AND repos.architecture=%s GROUP BY distros.name, repos.branch, YEAR(crawls.time), MONTH(crawls.time), DAY(crawls.time)"
cur.execute(q,(arch,))

for row in cur:
  print row

import gtk
from utils import chart

window = gtk.Window()
window.set_default_size(500,300)
window.show()

graph = chart.LineChart()
data = {}
for name,branch,y,m,d,c in cur:
  k = (name,branch)
  if not data.has_key(k):
    data[k] = []
  if c==None:
    c=0
  elif c>300:
    c = 300
  else:
    c=int(c)
  data[k].append((datetime.datetime(y,m,d),c))

for k in data.keys():
  graph.add(k[0]+" "+k[1],data[k])

window.add(graph)
graph.show()


window.connect("destroy",lambda x: gtk.main_quit())

gtk.main()
