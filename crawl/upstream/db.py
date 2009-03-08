from .utils import helper
from .utils import parsers

NAME="db"

MIRROR="http://download-west.oracle.com/berkeley-db/"

def get_releases(last_crawl=None):
  pkgs = []
  info = helper.open_dir(MIRROR)
  if info==None:
    return []
  for d,fn,date in info:
    if not d and (last_crawl==None or date>last_crawl):
      rel = parsers.parse_filename(fn)
      if rel != None and "CD" not in rel[2] and "NC" not in rel[2]:
        rel[3] = date
        pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs
