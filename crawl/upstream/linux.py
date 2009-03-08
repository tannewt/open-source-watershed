from .utils import helper
from .utils import parsers

NAME="linux"

MIRROR="http://www.kernel.org/pub/linux/kernel/"
def get_releases(last_crawl=None):
  pkgs = []
  info = helper.open_dir(MIRROR)
  if info==None:
    return []
  for d,name,date in info:
    if d and name[0]=="v" and (last_crawl==None or date>last_crawl):
      p_info = helper.open_dir(MIRROR+name)
      if p_info == None:
        continue
      for d2,n2,date2 in p_info:
        if not d2 and (last_crawl==None or date2>last_crawl):
          rel = parsers.parse_filename(n2)
          if rel != None and rel[0]=="linux":
	          rel[3] = date2
	          pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs
