import ftplib
import time
import datetime
import os
import urllib
import gzip
import sys
from .utils import helper

BRANCH_ETCH="etch"
BRANCH_LENNY="lenny"
BRANCH_SARGE="sarge"
BRANCH_SID="sid"
BRANCH_EXPERIMENTAL="experimental"

BRANCHES = [
  BRANCH_ETCH,
  BRANCH_LENNY,
  BRANCH_SARGE,
  BRANCH_SID,
  BRANCH_EXPERIMENTAL]

MIRROR = "debian.osuosl.org"

START_DIR = "debian/dists/"

def get_repos():
  ftp = ftplib.FTP(MIRROR)
  ftp.login()
  
  ftp.cwd(START_DIR)

  distros = []
  codename = None
  architectures = None
  components = None
  for branch in BRANCHES:
    release_file = []
    #print "fetching", branch
    ftp.retrlines('RETR %s'%(branch+"/Release"), release_file.append)
    time.sleep(1)
    # wait while we get the part we need
    while len(release_file)<9:
      time.sleep(1)
    
    #print "parsing"
    
    for line in release_file[:9]:
      name, value = line.split(":")[:2]
      #print name
      if name == "Suite":
        branch=line.split(' ')[1]
      elif name == "Codename":
        codename=line.split(' ')[1]
      elif name == "Architectures":
        architectures=line.split(' ')[1:]
      elif name == "Components":
        components=line.split(' ')[1:]
    
    if not branch or not codename or not architectures or not components:
      print "Something is missing from debian %s"%branch
    else:
      for arch in architectures:
        for comp in components:
          distros.append(["debian", branch, codename, comp, arch, None, None])
  
  #print distros
  ftp.quit()
  return distros

def crawl_repo(repo):
  pkgs = []
  name, branch, codename, comp, arch, last_crawl, new = repo
  #print "downloading"
  this_time = datetime.datetime.now()
  filename = "files/debian/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(time.mktime(this_time.timetuple())) + ".gz"
  this_time = helper.open_url("http://" + MIRROR + "/" + START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.gz",filename,last_crawl)
  #print "downloaded", filename
  
  if this_time==None:
    return pkgs
  
  #check to see if things have changed
  if last_crawl and this_time<last_crawl:
    #print "skipping",name,codename,comp,arch,"because it hasn't changed"
    return pkgs
  gzp = gzip.open(filename)

  this_name = None
  pkg = {}

  for line in gzp:
    line = line.strip("\n")
    if line == "":
      #[epoch:]upstream_version[-debian_revision] 
      if ":" in pkg["Version"]:
        epoch, rest = pkg["Version"].split(":",1)
      else:
        rest = pkg["Version"]
        epoch = 0
    
      if "-" in rest:
        rest, debv = rest.rsplit("-",1)
      else:
        debv = 0
      
      pkg["Description"] = "".join(pkg["Description"])
      # name, version, revision, time, additional
    
      pkgs.append([pkg["Package"], rest, debv, this_time, str(pkg)])
    elif line.startswith("Description"):
      name, value = line.split(":",1)
      pkg["Description"] = [value.strip()]
    elif line.startswith((" ","\t")):
      pkg["Description"].append(line)
    else:
      try:
        name, value = line.split(":",1)
        pkg[name] = value.strip()
        this_name = name
      except:
        print "ERROR: bad package line:",line
        return None
  
  return pkgs

