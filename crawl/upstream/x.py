from .utils import helper

NAME="x"

MIRROR="http://xorg.freedesktop.org/releases/"

DEADENDS = ["unsupported/"]

def parse_fn(fn):
  if fn.endswith(".tar.gz"):
    trimmed = fn[:-7]
  elif fn.endswith(".tar.bz2"):
    trimmed = fn[:-8]
  else:
    return None
  if "-" not in trimmed:
      return None
  pkg,ver = trimmed.rsplit("-",1)
  if "X11R7" in pkg:
    pkg, z = pkg.rsplit("-",1)
  rel = [pkg,0,ver,None,None]
  return rel
  
def explore(url, last_crawl):
  #print url
  pkgs = []
  info = helper.open_dir(url)
  if info==None:
    return []
  for d,name,date in info:
    if last_crawl!=None and date<last_crawl:
      continue
    if d and name not in DEADENDS and not name.startswith("X11R6") and not name.startswith("X10"):
      pkgs += explore(url+name, last_crawl)
    else:
      rel = parse_fn(name)
      if rel!=None:
        rel[-2] = date
        #print rel
        pkgs.append(rel)
  pkgs += explore(url+"src/", last_crawl)
  return pkgs
  
def get_releases(last_crawl=None):
  return explore(MIRROR, last_crawl)
