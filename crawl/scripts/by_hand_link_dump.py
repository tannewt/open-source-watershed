import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()
AHOST, AUSER, APASSWORD, ADB = helper.mysql_settings("abstract")

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB) 
cur = con.cursor()

acon = mysql.connect(host=AHOST,user=AUSER,passwd=APASSWORD,db=ADB) 
acur = acon.cursor()

cur.execute("SELECT package_id1, package_id2, strength FROM links, link_sources WHERE link_source_id=link_sources.id AND link_sources.description='By hand.'")

acur.execute("SELECT id FROM link_sources WHERE link_sources.description='By hand.'")
by_hand = acur.fetchone()[0]

for id1, id2, strength in cur:
  cur.execute("SELECT name FROM packages WHERE id = %s",(id1,))
  name1 = cur.fetchone()[0]
  acur.execute("SELECT id FROM packages WHERE name = %s",(name1,))
  aid1 = acur.fetchone()[0]
  
  cur.execute("SELECT name FROM packages WHERE id = %s",(id2,))
  name2 = cur.fetchone()[0]
  acur.execute("SELECT id FROM packages WHERE name = %s",(name2,))
  aid2 = acur.fetchone()[0]
  
  acur.execute("SELECT COUNT(*) FROM links WHERE package_id1=%s AND package_id2=%s AND link_source_id=%s",(aid1,aid2,by_hand))
  if acur.fetchone()[0]==0:
    acur.execute("INSERT INTO links (package_id1, package_id2, strength, link_source_id) VALUES (%s, %s, %s, %s)", (aid1, aid2, strength, by_hand))
    print ",".join((name1,name2,str(strength)))

acon.close()
con.close()
