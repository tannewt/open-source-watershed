import ftplib
import time
import datetime
import os
import urllib
import bz2
import sys
from .utils import helper

BRANCH_DAPPER="dapper"
BRANCH_FEISTY="feisty"
BRANCH_GUTSY="gutsy"
BRANCH_HARDY="hardy"
BRANCH_INTREPID="intrepid"
BRANCH_JAUNTY="jaunty"

BRANCHES = [
  BRANCH_DAPPER,
  BRANCH_FEISTY,
  BRANCH_GUTSY,
  BRANCH_HARDY,
  BRANCH_INTREPID]

MIRROR = "ubuntu.osuosl.org"

FTP_START_DIR = "pub/ubuntu/dists/"

HTTP_START_DIR = "ubuntu/dists/"

def get_repos():
  ftp = ftplib.FTP(MIRROR)
  ftp.login()
  
  ftp.cwd(FTP_START_DIR)

  distros = []
  codename = None
  architectures = None
  components = None
  branches = []
  for b in BRANCHES:
    branches.append(b)
    for repo in ["backports","proposed","security","updates"]:
      branches.append(b+"-"+repo)
  
  for branch in branches:
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
        architectures=["amd64","i386","powerpc","sparc"]
      elif name == "Components":
        components=line.split(' ')[1:]
    
    if not branch or not codename or not architectures or not components:
      print "Something is missing from ubuntu %s"%branch
    else:
      for arch in architectures:
        for comp in components:
          distros.append(["ubuntu", branch, codename, comp, arch, None, None])
  
  #print distros
  ftp.quit()
  return distros

def crawl_repo(repo):
  pkgs = []
  name, branch, codename, comp, arch, last_crawl, new = repo
  #print "downloading"
  this_time = time.time()
  url = "http://" + MIRROR + "/" + HTTP_START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.bz2"
  filename = "files/ubuntu/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(this_time) + ".bz2"
  #print url
  info = helper.open_url(url, filename, last_crawl)
  #print "downloaded", filename
  
  if info!=None:
    this_time = info
  else:
    return pkgs
  
  bzp = bz2.BZ2File(filename)

  this_name = None
  pkg = {}

  i = 1
  joins = []
  for line in bzp:
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
      
      for join in joins:
        pkg[join] = "".join(pkg[join])
      joins = []
      # name, version, revision, time, additional
    
      pkgs.append([pkg["Package"], rest, debv, this_time, str(pkg)])
      pkg = {}
    elif line.startswith((" ","\t")):
      try:
        pkg[this_name].append(line)
      except:
        pkg[this_name] = [pkg[this_name],line]
        joins.append(this_name)
    else:
      try:
        name, value = line.split(":",1)
        pkg[name] = value.strip()
        this_name = name
      except:
        print
        print "ERROR: bad package line:",line
        return None
    i += 1
  
  return pkgs
