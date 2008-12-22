from .utils import helper

NAME="gnome"

MIRROR="http://ftp.gnome.org/pub/gnome/sources/"
def get_releases(last_crawl=None):
  pkgs = []
  info = helper.open_dir(MIRROR)
  for d,name,date in info:
    if d:
      print name
      p_info = helper.open_dir(MIRROR+name)
      for d2,n2,date2 in p_info:
        if d2:
          ver_info = helper.open_dir(MIRROR+name+n2)
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
