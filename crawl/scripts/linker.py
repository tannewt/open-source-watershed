import sys
import os
import MySQLdb as mysql

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

if len(sys.argv)<2:
  print sys.argv[0],"<cmd>"

cmd = sys.argv[1]
con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()

BY_HAND_LINK_ID = 5

if cmd == "list":
  cur.execute("SELECT p1.name, p2.name FROM packages AS p1, packages AS p2, links WHERE p1.id = links.package_id1 AND p2.id = links.package_id2 AND links.link_source_id = %s ORDER BY p1.name, p2.name",(BY_HAND_LINK_ID,))
  for p1, p2 in cur:
    print p1,"<--",p2
elif cmd == "link":
  cur.execute("INSERT INTO links (package_id1, package_id2, link_source_id) VALUES ((SELECT id FROM packages WHERE name=%s),(SELECT id FROM packages WHERE name=%s), %s)",(sys.argv[2],sys.argv[3],BY_HAND_LINK_ID))
elif cmd == "unlink":
  pass
else:
  print "list -- lists all handmade links"
  print "link <p1> <p2> -- link p1 and p2 by hand"
  print "unlink <p1> <p2> -- unlink p1 and p2"

con.commit()
con.close()
