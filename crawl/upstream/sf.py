from .utils import helper
from .utils import parsers
import time
import re
import datetime

NAME="sourceforge"

PROJECTS = [ 20003, #aa project
             33140, #acpid
             30, #afterstep
             6235, #audacity
             40696, #blackbox
             26089, #bridge-utils
             #13554, #cinelerra
             2171, #cdrdao
             4664, #cscope
             42641, #digikam
             52551, #dosbox
             2406, #e2fsprogs
             #2, #enlightenment
             #9028, #firebird
             13478, #flac
             97492, #flex
             35398, #fluxbox
             3157, #freetype
             121684, #fuse
             31, #icewm
             1897, #ghostscript
             3242, #gkernel
             192, #gnucash
             115843, #gparted
             2055, #gnuplot
             4050, #gqview
             1537, #gutenprint
             136732, #hdparm
             149981, #hplip
             24099, #ImageMagick
             93438, #inkscape
             23475, #joe
             26279, #lcms
             65237, #libcddb
             12272, #libexif
             8874, #libgphoto2
             67873, #libgpod
             5635, #libmng
             32528, #libnjb
             158745, #libmtp
             29314, #libieee1284
             1674, #libusb
             106542, #libvisual
             10501, #libwmf
             62662, #libwpd
             26138, #k3b
             86937, #kaffeine
             80184, #krecipes
             12349, #mad
             106236, #mailx
             4286, #mhash
             4626, #mtx
             195, #mutt
             6208, #nasm
             14, #nfs-utils
             93482, #ndiswrapper
             8642, #netatalk
             12694, #net-snmp
             5128, #netpbm
             13956, #ntfsprogs
             8960, #obexftp
             #23067, #phpmyadmin
             235, #pidgin
             24366, #rdesktop
             108454, #scim
             #125235, #scribus
             7768, #slrn
             64297, #smartmontools
             10706, #sox
             311, #squuirrelmail
             2861, #strace
             44427, #sysfsutils
             #10894, #tcl
             #14067, #tightvnc
             3581, #usbutils
             17457, #webmin
             67268, #xdtv
             19869, #xfce
             9655, #xine-lib
             15273] #psmisc
             
             
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

GOOD_PACKAGES = ["e2fsprogs", "e2fsprogs-libs", "dosbox", "digikam", "blackbox", "audacity", "libAfterImage", "AfterStep", "libAfter", "libAfterBase", "freetype", "fluxbox", "flex", "inkscape", "gparted", "gnucash", "ghostscript", "icewm", "pidgin", "netatalk", "ndiswrapper", "kaffeine", "squirrelmail", "skim", "scim-qtimm", "scim-pinyin", "scim-tables", "scim-hangul", "scim-input-pad", "scim-m17n", "scim-uim", "scim-bridge", "scim", "usermin", "webmin", "xdtv", "xfce", "xine-lib", "xine-plugin", "gxine", "xine-ui", "psmisc", "aalib", "acpid", "bridge-utils", "cdrdao", "cscope", "ethtool", "flac", "fuse", "gnuplot", "gqview", "gutenprint", "hdparm", "hplip", "ImageMagick", "joe", "lcms", "libcddb", "libexif", "libgphoto2", "gtkpod", "libgpod", "libid3tag", "libmad", "madplay", "libieee1284", "libmng", "libmtp", "libnjb", "libusb", "libvisual", "libvisual-plugins", "libwmf", "libwpd", "mailx", "mhash", "mtx", "mutt", "nasm", "net-snmp", "netpbm", "nfs-utils", "ntfsprogs", "obexftp", "rdesktop", "slrn", "smartmontools", "sox", "strace", "sysfsutils", "usbutils", "krecipes" ]

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
      if rel!=None and rel[2]=="0.45+0.46pre3":
        rel[2]="0.45"
      
      if rel!=None and rel[0] in GOOD_PACKAGES and ".slack." not in rel[2]:
        rel[-2] = f[1]
        rels.append(rel)
        #print "GOOD",rel
      elif rel!=None:
        #print "BAD ", rel
        pass
  return rels
