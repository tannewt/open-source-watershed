import sqlite3
import datetime
import time
import subprocess
from .utils import helper

MIRROR = "mirror.cs.vt.edu"
HTTP_START_DIR = "pub/SabayonLinux"
FTP_START_DIR = None

VERSIONS = ["3.5", "4"]
CURRENT = "3.5"
FUTURE = "4"

ARCHES = ["amd64", "x86"]

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos():
  repos = []
  for v in VERSIONS:
    for a in ARCHES:
      branch = "past"
      if v==CURRENT:
        branch = "current"
      elif v==FUTURE:
        branch = "future"
      repos.append(["sabayon", branch, v, "", a, None, None])
  return repos

# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
  distro,branch,codename,component,arch,last_crawl,new = repo
  
  fn = "".join(("files/sabayon/packages-",codename,"-",arch,"-",str(time.time()),".db"))
  url = "".join(("http://",MIRROR,"/",HTTP_START_DIR,"/entropy/standard/sabayonlinux.org/database/",arch,"/",codename,"/packages.db.bz2"))
  
  #print "open url"
  t = helper.open_url(url,fn+".bz2",last_crawl)
  
  if t==None:
    return []
  
  #print "extract"
  try:
    p = subprocess.Popen(("/bin/bunzip2",fn+".bz2"),stdout=None)
    x = p.wait()
  except OSError, e:
    print e
    x=-1
  
  #print "sql stuff"
  conn = sqlite3.connect(fn)
  c = conn.cursor()
  #print "go sql"
  c.execute("SELECT baseinfo.name, baseinfo.version, baseinfo.revision, baseinfo.branch, extrainfo.datecreation FROM baseinfo, extrainfo WHERE baseinfo.idpackage = extrainfo.idpackage;")
  #print "sql done"
  
  pkgs = []
  for name, version, revision, branch, date in c:
    dt = datetime.datetime.fromtimestamp(float(date))
    if last_crawl==None or last_crawl<dt:
      if "-" == version[-3]:
        version, gentoo_revision = version.rsplit("-")
        revision = gentoo_revision[1:] + "." + revision
      pkgs.append([name, version, revision, 0, dt, ""])
  return pkgs
