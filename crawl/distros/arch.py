import subprocess
import time
import datetime
import os
from .utils import helper

MIRROR = "ftp.archlinux.org"
HTTP_START_DIR = None
FTP_START_DIR = None

ARCHES = ["i686","x86_64"]

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos():
  repos = []
  for comp in ["core","extra"]:
    for a in ARCHES:
      repos.append(["arch","current","",comp,a,None,None])
  
  for comp in ["testing"]:
    for a in ARCHES:
      repos.append(["arch","future","",comp,a,None,None])
  
  for comp in ["community"]:
    for a in ARCHES:
      repos.append(["arch","experimental","",comp,a,None,None])
  
  return repos

# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
  distro,branch,codename,component,arch,last_crawl,new = repo
  pkgs = []
  fn = "".join(("files/arch/",component,"-",str(time.time()),".db.tar.gz"))
  url = "".join(("http://",MIRROR,"/",component,"/os/",arch,"/",component,".db.tar.gz"))
  new_dir = "".join(("files/arch/",component,"-",str(time.time()),"/"))
  os.mkdir(new_dir)
  t = helper.open_url(url,fn,last_crawl)
  if t:
    try:
      #print " ".join(("/bin/tar","-xzf ",fn,"-C",new_dir))
      p = subprocess.Popen(("/bin/tar","-xzf",fn,"-C",new_dir),stdout=None)
      x = p.wait()
    except OSError, e:
      print e
      x=-1
    
    for d in os.listdir(new_dir):
      fn = "".join((new_dir,d,"/desc"))
      try:
        last = os.stat(fn)
      except OSError:
        print "no cache"
        last = None
      
      if last:
        last = last.st_mtime
        last = datetime.datetime.fromtimestamp(last)
      
      # ignore if its not new
      if last and last_crawl!=None and last<last_crawl:
        continue
      
      pkg = {}
      key = None
      for line in open(fn):
        if line[0]=="%":
          key = line.strip("\n%")
          pkg[key] = []
        elif line=="\n":
          if key:
            pkg[key] = "".join(pkg[key]).strip()
          key = None
        else:
          pkg[key].append(line)
      
      version, revision = pkg["VERSION"].rsplit("-",1)
      if " " in pkg["BUILDDATE"]:
        try:
          released = datetime.datetime.strptime(pkg["BUILDDATE"],"%a %b %d %H:%M:%S %Y")
        except:
          #print "ERROR: cannot parse",pkg["BUILDDATE"]
          pass
      else:
        released = datetime.datetime.fromtimestamp(long(pkg["BUILDDATE"]))
      
      pkgs.append([pkg["NAME"],version,revision,0,released,str(pkg)])
  return pkgs
