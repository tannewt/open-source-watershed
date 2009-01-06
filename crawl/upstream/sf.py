from .utils import helper
from .utils import parsers
import time
import re
import datetime

NAME="sourceforge"

PROJECTS = [ 30, #afterstep
             6235, #audacity
             40696, #blackbox
             13554, #cinelerra
             42641, #digikam
             52551, #dosbox
             2406, #e2fsprogs
             2, #enlightenment
             #9028, #firebird
             97492, #flex
             35398, #fluxbox
             3157, #freetype
             31, #icewm
             1897, #ghostscript
             192, #gnucash
             115843, #gparted
             93438, #inkscape
             26138, #k3b
             86937, #kaffeine
             93482, #ndiswrapper
             8642, #netatalk
             23067, #phpmyadmin
             235, #pidgin
             108454, #scim
             125235, #scribus
             311, #squuirrelmail
             #10894, #tcl
             #14067, #tightvnc
             17457, #webmin
             67268, #xdtv
             19869, #xfce
             9655] #xine-lib
             
BAD_FNS = {235: ["gtk"],
           67268: [".orig.","patch"],
           2406: ["WIP"],
           52551: ["linux-x86"],
           30: ["noimages"],
           19869: ["menushadow","rpm"],
           311: ["old","_","ar-","locales","ug-","ka-","fy-"],
           108454: ["fcitx"],
           13554: ["ubuntu"],
           6235: ["linux-i386","debian"]}

def get_files(project_id,last_crawl=None):
  limit = 10
  if last_crawl==None:
    limit = 100
  
  fn = "files/sourceforge/%d-%s.rss"%(time.time(),project_id)
  helper.open_url("http://sourceforge.net/export/rss2_projfiles.php?group_id=%s&rss_limit=%s"%(project_id,limit),fn)
  
  pattern_file = re.compile("(\S*) \([0-9]* bytes, [0-9]* downloads to date\)")
  pattern_date = re.compile("<pubDate>(.*)</pubDate>")
  
  files = []
  fs = []
  for line in open(fn):
    tmp_fs = pattern_file.findall(line)
    if len(tmp_fs)>0:
      fs=tmp_fs
    ds = pattern_date.findall(line)
    if len(ds)>0:
      d = datetime.datetime.strptime(ds[0],"%a, %d %b %Y %H:%M:%S %Z")
      for f in fs:
        files.append((f,d))
        fs = []
  return files

def contains(s, parts):
  for p in parts:
    if p in s:
      return True
  return False
  
def get_releases(last_crawl=None):
  rels = []
  for project in PROJECTS:
    files = get_files(project, last_crawl)
    for f in files:
      if BAD_FNS.has_key(project) and contains(f[0],BAD_FNS[project]):
        continue
      rel = parsers.parse_filename(f[0])
      if rel!=None:
        rel[-2] = f[1]
        rels.append(rel)
  return rels
