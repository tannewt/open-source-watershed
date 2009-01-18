from .utils import helper
from .utils import parsers

NAME="gimp"

MIRROR="http://ftp.esat.net/mirrors/ftp.gimp.org/pub/gimp/"

DEADENDS = ["contrib/","extras/","fonts/","help/","historical/","net-fu/","plug-ins/","plugin-template/","stable/", "v0.99.pre11/"]
  
def explore(url, last_crawl):
  #print url
  pkgs = []
  info = helper.open_dir(url)
  if info==None:
    return []
  for d,name,date in info:
    if last_crawl!=None and date<last_crawl:
      continue
    if d and name not in DEADENDS:
      pkgs += explore(url+name, last_crawl)
    else:
      rel = parsers.parse_filename(name)
      if rel!=None:
        rel[-2] = date
        #print rel
        pkgs.append(rel)
  return pkgs
  
def get_releases(last_crawl=None):
  return explore(MIRROR, last_crawl)
