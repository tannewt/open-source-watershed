import time
import datetime
import os
import urllib
import bz2
import sys
import MySQLdb as mysql

sys.path.append(os.getcwd())

from utils import helper,deb
MIRROR = "ubuntu.osuosl.org"

FTP_START_DIR = "pub/ubuntu/dists/"

HTTP_START_DIR = "ubuntu/dists/"

def version_parser(version):
  #[epoch:]upstream_version[-debian_revision] 
  if ":" in version:
    epoch, rest = version.split(":",1)
  else:
    rest = version
    epoch = 0

  if "-" in rest:
    rest, debv = rest.rsplit("-",1)
  else:
    debv = 0
  return epoch, rest, debv
p_map = {}

for comp in ["main","multiverse","restricted","universe"]:
  url = "http://" + MIRROR + "/" + HTTP_START_DIR + "intrepid/" + comp + "/source/Sources.bz2"
  filename = "files/ubuntu/Sources-intrepid-" + comp + "-" + str(time.time()) + ".bz2"
  
  info = helper.open_url(url, filename)
  pkgs = deb.parse_packages(version_parser, filename, url)
  
  for p in pkgs:
    p = eval(p[-1])
    if not p.has_key("Package") or not p.has_key("Binary"):
      continue
    
    if not p_map.has_key(p["Package"]):
      p_map[p["Package"]] = []
    
    p_map[p["Package"]]+=p["Binary"].split(", ")

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()

for upstream in p_map.keys():
  print "updating",upstream
  q = "SELECT id FROM packages WHERE name=%s"
  cur.execute(q,(upstream))
  try:
    i = cur.fetchone()[0]
  except:
    q = "INSERT INTO packages (name) VALUES (%s)"
    cur.execute(q,(upstream))
    cur.execute("select last_insert_id();")
    i = cur.fetchone()[0]
  
  for downstream in p_map[upstream]:
    if downstream != upstream:
      print "found",downstream
      cur.execute("UPDATE packages SET source_id=%s WHERE name=%s",(i,downstream))
  con.commit()
con.close()
      
