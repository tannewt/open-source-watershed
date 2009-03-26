import sys
import os

sys.path.append(os.getcwd())

from utils import helper
from utils import parsers

NAME="apache"

MIRROR="http://archive.apache.org/dist/"

GOOD = ["apache","mod_python"activemq-cpp apr apr-iconv apr-util cocoon hadoop lucene nutch maven mina mod_perl Mail-SpamAssassin tapestry ]

de = open("upstream/apache_deadends.txt")
DEADENDS = map(lambda s: s.strip()+"/", de.readlines())
de.close()

DEADENDS.append("cgi/")
DEADENDS.append("harmony/")
DEADENDS.append("incubator/")
win32-bin/

RENAME = {"httpd":"apache"}
  
def explore(url, last_crawl):
  pkgs = []
  print url
  info = helper.open_dir(url)
  if info==None:
    return []
  for d,name,date in info:
    if last_crawl!=None and date<last_crawl:
      continue
    if d and name not in DEADENDS:
      pkgs += explore(url+name, last_crawl)
    else:
      if name.startswith("apache"):
        rel = parsers.parse_filename(name,sep="_")
      else:
        rel = parsers.parse_filename(name)
      if rel!=None:
        rel[-2] = date
        if rel[0] in RENAME:
          rel[0] = RENAME[rel[0]]
        print rel[0],rel[2]
        if rel[0] in GOOD:
          pkgs.append(rel)
  return pkgs
  
def get_releases(last_crawl=None):
  return explore(MIRROR, last_crawl)

if __name__=="__main__":
  pkgs = get_releases()
  print
  print
  for p in pkgs:
    print p[0],p[2],p[-2]
