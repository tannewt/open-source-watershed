import MySQLdb as mysql
import sys
import os
import xml.etree.ElementTree as xml

sys.path.append(os.getcwd())

from utils import helper
from utils.progressbar.progressbar import ProgressBar

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()
pkgs = {}
homepages = {}
if len(sys.argv)>1:
  for p in sys.argv[1:]:
    cur.execute("SELECT id FROM packages WHERE name=%s",(p,))
    row = cur.fetchone()
    if row!=None:
      pkgs[row[0]] = p
  days = None
else:
  cur.execute("SELECT id, name FROM packages")
  for i,name in cur:
    pkgs[i] = name

#print pkgs

distros = {}
distro_ids = {}
cur.execute("SELECT id, name FROM distros")
for i,name in cur:
  distros[i] = name
#print distros

#pb = ProgressBar()
i = 0
for p in pkgs.keys():
  #pb.render(100*i/len(pkgs),"\n%d/%d"%(i,len(pkgs)))
  i+=1
  #print pkgs[p]
  for d in distros:
    cur.execute("SELECT extra.content FROM extra,releases,repos WHERE releases.package_id = %s AND repos.distro_id=%s AND releases.repo_id=repos.id AND extra.release_id=releases.id AND extra.content!=''",(p,d))
    #row = cur.fetchone()
    #print distros[d],"\t",
    for row in cur:
      #if p not in homepages:
      #  homepages[p] = []
      if distros[d] == "ubuntu":
        r = eval(row[0])
        if "Homepage" in r:
          print pkgs[p],r["Homepage"]
          break
      elif distros[d] == "arch":
        r = eval(row[0])
        if "URL" in r:
          print pkgs[p],r["URL"]
          break
      elif distros[d] == "slackware":
        r = eval(row[0])
        if "description" in r:
          w = filter(lambda x: x.startswith("http://"),r["description"].split())
          if len(w)>0:
            print pkgs[p],w[0]
          break
      elif distros[d] == "gentoo" or distros[d]=="funtoo":
        r = eval(row[0])
        if "HOMEPAGE" in r:
          print pkgs[p],r["HOMEPAGE"]
          break
      elif distros[d] == "fedora":
        try:
          repomd_tree = xml.fromstring(row[0])
        except Exception:
          continue
        datas = repomd_tree.findall("{http://linux.duke.edu/metadata/common}url")
        if len(datas)>0:
          print pkgs[p],datas[0].text
          break
      else:
        #print row
        break
    #print
  #print
con.close()

#print len(rev),"sites",len(pkgs),"packages"
