import urllib
import ftplib
import time
import datetime
from .utils import helper

MIRROR="slackware.osuosl.org"
FTP_START_DIR="pub/slackware/"
HTTP_START_DIR="/"

def get_repos():
  ftp = ftplib.FTP(MIRROR)
  ftp.login()
  
  ftp.cwd(FTP_START_DIR)
  files = ftp.nlst()
  releases = []
  for f in files:
    if f.count("-")==1:
      releases.append(f)
  
  comps = []
  releases.remove("slackware-3.3")
  rs = []
  for r in releases:
    #print r
    r = r.split("-")[1]
    if r!="current":
      rs.append(float(r))
  
  for r in ["current"]+rs:
    if r=="current":
      branch = "future"
    elif r==max(rs):
      branch = "current"
      r = "%2.1f"%r
    else:
      r = "%2.1f"%r
      branch = "past"
    for comp in ["extra","pasture","patches","slackware"]:
      comps.append([branch,r,comp])
    
  repos = map(lambda x: ["slackware", x[0], x[1], x[2], "i486", None, None], comps)
  ftp.quit()
  
  return repos
  
def crawl_repo(repo):
  name, branch, codename, comp, arch, last_crawl, new = repo
  
  this_time = time.time()
  filename = "files/slackware/PACKAGES-" + codename + "-" + comp + "-" + str(this_time) + ".TXT"
  this_time = helper.open_url("http://" + MIRROR + HTTP_START_DIR + "slackware-" + codename + "/" + comp + "/PACKAGES.TXT",filename, last_crawl)
  
  pkgs = []
  
  if this_time==None:
    return pkgs
  
  #check to see if things have changed
  if last_crawl and this_time<last_crawl:
    #print "skipping",name,codename,comp,arch,"because it hasn't changed"
    return pkgs
  
  if comp=="slackware":
    k_filename = "files/slackware/VERSIONS-" + codename + "-" + str(time.mktime(this_time.timetuple())) + ".TXT"
    k_time = helper.open_url("http://" + MIRROR + HTTP_START_DIR + "slackware-" + codename + "/kernels/VERSIONS.TXT",k_filename)
  
    kernel = open(k_filename).readlines()[1]
    kernel = kernel.split()
    kernel = kernel[kernel.index('version')+1].strip(".").strip(",")
    # name, version, revision, time, additional
    pkgs.append(["linux", kernel, None, 0, this_time, None])
  
  pkg_file = open(filename)
  header = True
  last_empty = None
  pkg = {}
  for line in pkg_file:
    line = line.strip()
    
    if last_empty==None:
      if "html" in line or "HTML" in line:
        print
        print "bad url:",filename
        break;
      last_empty=False
    
    if header:
      this_empty = line==""
      header = not (last_empty and this_empty)
      last_empty = this_empty
    else:
      if line=="":
        if len(pkg.keys())>0:
          pkg["description"] = "".join(pkg["description"])
          pkgs.append([pkg["name"],pkg["version"],pkg["revision"],0,this_time,str(pkg)])
          pkg = {}
        continue
      else:
        name, value = line.split(":",1)
      
      if name=="PACKAGE NAME":
        pkg["name"],pkg["version"],pkg["arch"],pkg["revision"]=value.strip()[:-4].rsplit("-",3)
      elif name==pkg["name"] or name=="PACKAGE DESCRIPTION":
        if pkg.has_key("description"):
          pkg["description"].append(value.strip()+"\n")
        else:
          pkg["description"] = [value.strip()]
      else:
        pkg[name] = value.strip()
    
  return pkgs
