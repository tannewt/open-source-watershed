import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper
from utils.timeline import *

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = True
VERBOSE_RESULT = False

UPSTREAM_NOTES = False

def get_upstream(con, package):
  cur = con.cursor()
  #print "query upstream"
  q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' AND releases.repo_id IS NULL GROUP BY releases.version ORDER BY MIN(releases.released)"
  cur.execute(q,(package,))
  if cur.rowcount == 0:
    if VERBOSE:
      print "falling back to approximate upstream"
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,))
  
  upstream = Timeline()
  if VERBOSE:
    print "upstream"
  for version,date in cur:
    if VERBOSE:
      print version,date
    upstream[date] = version
  
  return upstream

def get_downstream(con, distro, package, branch=None, arch=None, now=None):
  cur = con.cursor()
  if branch==None and arch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro))
  elif branch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.architecture=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,arch))
  elif arch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.branch=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,branch))
  else:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.architecture=%s AND repos.branch=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,arch,branch))

  downstream = Timeline()
  if VERBOSE:
    print "downstream"
  for version, date in cur:
    if VERBOSE:
      print version, date
    downstream[date] = version

  if VERBOSE:
    print
  return downstream

def get_package_age(distro, package, branch=None, arch=None, now=None):
  con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
  upstream = get_upstream(con, package)
  downstream = get_downstream(con, distro, package, branch, arch, now)
  ms = timedelta(microseconds=1)
  upstreams = {}
  latest = []
  age = ConnectedTimeline()
  last_downstream = None
  ds = False
  u = 0
  d = 0
  #print
  #print "interleave"
  #interleave the dates
  while u+d < len(upstream)+len(downstream):
    is_u = False
    version = None
    date = None
    append = False
    if u<len(upstream) and (len(downstream)==d or upstream[u][0]<=downstream[d][0]):
      if VERBOSE:
        print "upstream",upstream[u]
      date, version = upstream[u]
      upstreams[version] = date
      is_u = True
      append = len(downstream)==d or upstream[u][0]!=downstream[d][0]
      u+=1
    else:
      if VERBOSE:
        print "downstream",downstream[d]
      date, version = downstream[d]
      last_downstream = version
      append = True
      d+=1
    if ds and append:
      if len(latest)==0:
        age[date] = date-date
      else:
        age[date] = date-upstreams[latest[0]]
    if is_u:
      latest.append(version)
      #print latest
    else:
      while len(latest)>0  and latest.pop(0)!=version:
        pass
      #print latest
    if last_downstream!=None and append:
      ds=True
        
      if len(latest)==0:
        age[date+ms] = date-date
      else:
        age[date+ms] = date-upstreams[latest[0]]
  #print
  #print "age"
  if now==None:
    now = datetime.now()
  if last_downstream!=None:
    if len(latest)==0:
      age[now] = now-now
    else:
      age[now] = now-upstreams[latest[0]]
  
  if VERBOSE or VERBOSE_RESULT:
    print "age of",package
    for a in age:
      print a
    print
  return upstream,downstream,age

if __name__=="__main__":
  gimp_upstream,gimp_downstream,gimp_age = get_package_age("gentoo", "gimp", "future")
  print gimp_age
