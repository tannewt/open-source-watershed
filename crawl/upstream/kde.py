try:
  from .utils import helper
  from .utils import parsers
except:
  import sys
  sys.path.append(".")
  from utils import helper
  from utils import parsers

NAME="kde"

MIRROR="http://mirror.cc.columbia.edu/pub/software/kde/"

DEADENDS = ["snapshots/", "FreeBSD/", "Mandrake/", "RedHat/", "SuSE/", "contrib/", "Conectiva/", "Mandriva/", "kubuntu/", "AIX/", "ArkLinux/", "Slamd64/", "Pardus/", "Slackware/", "windows/", "win32/", "Debian/", "Turbo/", "Mandrakelinux/", "adm/", "devel/", "doc/", "events/", "packages/", "printing/", "Pardus/", "mac/", "security_patches/", "kolab/", "icons/"]
  
def explore(url, last_crawl):
  print url
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
  return explore(MIRROR, None)

if __name__=="__main__":
  pkgs = get_releases()
  for p in pkgs:
    print p[0], p[2]
