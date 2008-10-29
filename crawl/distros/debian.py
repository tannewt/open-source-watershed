import time
import datetime
import os
import urllib
import gzip
import sys
from .utils import helper,deb

CN_ETCH="etch"
CN_LENNY="lenny"
CN_SARGE="sarge"
CN_SID="sid"
CN_EXPERIMENTAL="experimental"

CODENAMES = [
  CN_ETCH,
  CN_LENNY,
  CN_SARGE,
  CN_SID,
  CN_EXPERIMENTAL]

BRANCHES = {
  CN_ETCH : "lts",
  CN_LENNY : "future",
  CN_SARGE : "past",
  CN_SID : "current",
  CN_EXPERIMENTAL : "experimental"}

MIRROR = "debian.osuosl.org"

START_DIR = "debian/dists/"

def get_repos():
  distros = []
  codename = None
  architectures = None
  components = None
  this_time = datetime.datetime.now()
  for codename in CODENAMES:
    for x in [None, "proposed-updates"]:
      if x!=None:
        crawl = codename + "-" + x
      else:
        crawl = codename
      #print "fetching", branch
      filename = "files/debian/Release-"+crawl+"-"+str(time.mktime(this_time.timetuple()))
      if None==helper.open_url("".join(["http://",MIRROR,"/",START_DIR,crawl,"/Release"]),filename):
        continue
      
      #print "parsing"
      
      for line in open(filename).readlines()[:9]:
        line = line.strip()
        name, value = line.split(":")[:2]
        #print name
        if name == "Architectures":
          architectures=line.split(' ')[1:]
        elif name == "Components":
          components=line.split(' ')[1:]
      
      if not architectures or not components:
        print "Something is missing from debian %s"%branch
      else:
        for arch in architectures:
          for comp in components:
            if x:
              comp += "|" + x
            distros.append(["debian", BRANCHES[codename], codename, comp, arch, None, None])
  
  #print distros
  return distros

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

def crawl_repo(repo):
  name, branch, codename, comp, arch, last_crawl, new = repo

  if "|" in comp:
    comp, test = comp.split("|")
    codename += "-" + test
  
  filename = "files/debian/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(time.time()) + ".gz"
  url = "http://" + MIRROR + "/" + START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.gz"
  
  pkgs = deb.parse_packages(version_parser,filename,url,last_crawl)
  return pkgs

