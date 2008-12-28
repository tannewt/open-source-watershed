from .utils import helper

NAME="gnome"

MIRROR="http://ftp.gnome.org/pub/gnome/sources/"
def get_releases(last_crawl=None):
  pkgs = []
  info = helper.open_dir(MIRROR)
  if info==None:
    return []
  for d,name,date in info:
    if d and (last_crawl==None or date>last_crawl):
      print name
      p_info = helper.open_dir(MIRROR+name)
      if p_info == None:
        continue
      for d2,n2,date2 in p_info:
        if d2 and (last_crawl==None or date2>last_crawl):
          ver_info = helper.open_dir(MIRROR+name+n2)
          if ver_info == None:
            continue
          for di,fn,date3 in ver_info:
            if fn.endswith(".tar.bz2") and "-" in fn:
              pkg,ver = fn[:-8].rsplit("-",1)
              rel = [pkg,0,ver,date3,None]
              print rel
              pkgs.append(rel)
            elif fn.endswith(".tar.gz") and "-" in fn:
              pkg,ver = fn[:-7].rsplit("-",1)
              rel = [pkg,0,ver,date3,None]
              print rel
              pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs
