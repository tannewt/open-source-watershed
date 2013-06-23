import sys
import os
import bz2
import psycopg2 as db

sys.path.append(os.getcwd())
from utils import helper,deb

if len(sys.argv) <= 2:
  print sys.argv[0],"<distro>","<path>"

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = db.connect(host=HOST,user=USER,password=PASSWORD,database=DB)
cur = con.cursor()

distro = sys.argv[1]
path = sys.argv[2]
if distro == "ubuntu" or distro == "debian":
  f = bz2.BZ2File(path)
  pkgs = deb.parse_package_dict(f)
  for pkg in pkgs:
    print pkg["Package"]
    d = "<span id=\"ubuntu\">%s -From <a href=\"%s\">Ubuntu</a></span>" % (pkg["Description"], "http://packages.ubuntu.com/raring/" + pkg["Package"])
    cur.execute("SELECT id FROM packages WHERE name=%s", (pkg["Package"],))
    i = cur.fetchone()[0]
    cur.execute("SELECT id, description FROM package_info WHERE package_id=%s", (i,))
    print d
    h = None
    if "Homepage" in pkg:
      h = pkg["Homepage"]
    if cur.rowcount == 0:
      cur.execute("INSERT INTO package_info (package_id, _when, user_id, description, homepage) VALUES (%s, NOW(), 1, %s, %s)", (i, d, h))
    else:
      i, old_d = cur.fetchone()
      if old_d != None and "<span id=\"ubuntu\">" in old_d:
        d = old_d
      cur.execute("UPDATE package_info SET description=%s, homepage=%s WHERE id=%s", (d, h, i))
con.commit()
con.close()

