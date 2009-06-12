# -*- coding: utf-8 -*-
from .utils import helper
from .utils import parsers

NAME="gnome"

MIRROR="http://ftp.gnome.org/pub/gnome/sources/"
def get_releases(last_crawl=None):
  last_crawl = None
  pkgs = []
  info = helper.open_dir(MIRROR)
  if info==None:
    return []
  for d,name,date in info:
    if d and (last_crawl==None or date>last_crawl):
      #print name
      p_info = helper.open_dir(MIRROR+name)
      if p_info == None:
        continue
      for d2,n2,date2 in p_info:
        if d2 and (last_crawl==None or date2>last_crawl):
          ver_info = helper.open_dir(MIRROR+name+n2)
          if ver_info == None:
            continue
          for di,fn,date3 in ver_info:
            rel = parsers.parse_filename(fn)
            if rel != None:
  	          rel[3] = date3
  	          pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs
