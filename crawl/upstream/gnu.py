from .utils import helper

NAME="gnu"

MIRROR="http://ftp.gnu.org/gnu/"

DEADENDS = ["windows/","packages/","gnu-0.2/","Doc/"]

def has_alpha(s):
  for c in s:
    if c.isalpha():
      return True
  return False

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
  
  # filter out the bad stuff
  if pkg in ["mit"] or ver in ["latest", "wish", "AIX", "UX", "JDK1.2", "i386", "scheme_7.7.1.orig", "1.4.3.SPARC.2.8.pkg", "linux", "html", "build"] or (pkg.startswith("clisp") and (pkg!="clisp" or ver=="source")) or (pkg.startswith("mit-scheme") and pkg!="mit-scheme") or (pkg.startswith("bpel2owfn") and pkg!="bpel2owfn"):
    return None
  
  if len(ver)==1 or ver in ["src", "source"] or has_alpha(ver):
    if "-" not in pkg:
      return None
    pkg,ver2 = pkg.rsplit("-",1)
    if ver2 in ["bin","fix"]:
      return None
    if ver in ["src","source"]:
      ver = ""
    if pkg=="winboard":
      ver = ver2.replace("_",".")
    elif ver.isalpha():
      pkg += "-" + ver
      ver = ver2
    elif ver2.isalpha():
      pkg += "-" + ver2
    else:
      if ver!="":
        ver=ver2+"-"+ver
  rel = [pkg,0,ver,None,None]
  return rel
  
def explore(url, last_crawl):
  #print url
  pkgs = []
  info = helper.open_dir(url)
  if info == None:
    return []
  for d,name,date in info:
    if last_crawl!=None and date<last_crawl:
      continue
    if d and name not in DEADENDS:
      pkgs += explore(url+name, last_crawl)
    else:
      rel = parse_fn(name)
      if rel!=None:
        rel[-2] = date
        #print rel
        pkgs.append(rel)
  return pkgs
  
def get_releases(last_crawl=None):
  return explore(MIRROR, last_crawl)
