import MySQLdb as mysql
import sys
import os

# output an html table package name by distro name
# this ought to help identify relationships between package names
# across distros

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()

distros = []
cur.execute("SELECT id, name FROM distros ORDER BY id")
for id, name in cur:
  distros.append(name)

pkgs = {}
cur.execute("SELECT id, name, source_id FROM packages ORDER BY name")
keys = {}
for id, name, src in cur:
  pkgs[id] = [name, src, 0, [False]*len(distros),False]
  if not keys.has_key(name[0].lower()):
    keys[name[0].lower()] = []
  keys[name[0].lower()].append(id)

cur.execute("SELECT DISTINCT releases.package_id, repos.distro_id FROM releases, repos WHERE releases.repo_id = repos.id")
for pkg, distro in cur:
  pkgs[pkg][3][distro-1] = True
  pkgs[pkg][2]+=1

cur.execute("SELECT DISTINCT package_id FROM releases WHERE releases.repo_id IS NULL;")
for row in cur:
  pkgs[row[0]][4] = True

def links():
  k = keys.keys()
  k.sort()
  return "|".join(map(lambda s: "<a href=\"pkg_names_%s.html\">%s</a>"%(s,s), k))

def d():
  return "  <tr><td></td><td></td>" + "".join(map(lambda x: "<th>"+x+"</th>", distros)) + "</tr>"

def to_row(id,p):
  if p[4]:
    s = ["<tr><td><a name=\"%d\"><b>%s</b></a></td>"%(id,p[0])]
  else:
    s = ["<tr><td><a name=\"%d\">%s</a></td>"%(id,p[0])]
  if p[1]:
    s.append("<td class=\"%s\"><a href=\"#%d\">%d</a></td>"%(p[2],p[1],p[1]))
  else:
    s.append("<td class=\"%s\"></td>"%p[2])
  s += map(lambda x: "<td class=\"%s\"></td>"%x, p[3])
  s.append("</tr>")
  return "".join(s)

def to_int(x):
  if x:
    return 1
  return 0
    
for k in pkgs.keys():
  if sum(map(to_int, pkgs[k][3]))==len(pkgs[k][3]):
    print pkgs[k][0]

if "--html" in sys.argv:
  for k in keys:
    page = []
    page.append("<html>")
    page.append("<head>")
    page.append("  <title>Package Names vs. Distro</title>")
    page.append("  <style type=\"text/css\">")
    page.append("    .True { background-color: green; }")
    page.append("  </style>")
    page.append("</head>")
    page.append("")


    page.append("<body>")
    page.append(links())
    page.append("<table>")
    i = 0
    for key in keys[k]:
      if i%25==0:
        page.append(d())
      page.append(to_row(key,pkgs[key]))
      i+=1

    page.append("</table>")
    page.append("</body>")
    page.append("</html>")

    f = open("pkg_names_%s.html"%k,"w")
    f.writelines(map(lambda s: s+"\n",page))
    f.close()
