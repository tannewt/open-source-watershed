import time
import datetime
import os
import urllib
import bz2
import sys
from .utils import helper,deb

CN_DAPPER="dapper"
CN_FEISTY="feisty"
CN_GUTSY="gutsy"
CN_HARDY="hardy"
CN_INTREPID="intrepid"
CN_JAUNTY="jaunty"

CODENAMES = [
  CN_DAPPER,
  CN_FEISTY,
  CN_GUTSY,
  CN_HARDY,
  CN_INTREPID]

LTS = [CN_DAPPER, CN_HARDY]

ARCHES = {CN_DAPPER : ["amd64", "i386", "powerpc", "sparc"],
  CN_FEISTY : ["amd64", "i386", "powerpc", "sparc"],
  CN_GUTSY : ["amd64", "i386", "powerpc", "sparc"],
  CN_HARDY : ["amd64", "i386"],
  CN_INTREPID : ["amd64", "i386"]}

MIRROR = "ubuntu.osuosl.org"

FTP_START_DIR = "pub/ubuntu/dists/"

HTTP_START_DIR = "ubuntu/dists/"

def get_repos():
  repos = []
  for codename in CODENAMES:
    for repo in [None,"backports","proposed","security","updates"]:
      for arch in ARCHES[codename]:
        for component in ["main","multiverse","universe","restricted"]:
          if repo!=None:
            component += "|" + repo
          
          if codename == CODENAMES[-1]:
            branch = "future"
          elif codename == CODENAMES[-2]:
            branch = "current"
          elif codename in LTS:
            branch = "lts"
          else:
            branch = "past"
          
          repos.append(["ubuntu", branch, codename, component, arch, None, None])

  return repos

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
  
  url = "http://" + MIRROR + "/" + HTTP_START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.bz2"
  filename = "files/ubuntu/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(time.time()) + ".bz2"
  
  info = helper.open_url(url, filename, last_crawl)
  pkgs = deb.parse_packages(version_parser, filename, url, last_crawl)
  
  return pkgs
