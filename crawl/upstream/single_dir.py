try:
  from .utils import helper
  from .utils import parsers
except:
  import sys
  sys.path.append(".")
  from utils import helper
  from utils import parsers

NAME="single_dir"

SOURCES = {"ftp://pkg-shadow.alioth.debian.org/pub/pkg-shadow/": [["shadow"],[]],
           "ftp://ftp.cistron.nl/pub/people/miquels/sysvinit/": [["sysvinit"],[]],
           "http://www.infodrom.org/projects/sysklogd/download/": [["sysklogd"],[]],
           "ftp://ftp.astron.com/pub/file/" : [["file"],[]],
           "http://devresources.linux-foundation.org/dev/iproute2/download/": [["iproute2"],[]],
           "http://ftp.altlinux.org/pub/people/legion/kbd/": [["kbd"],["stable","testing"]],
           "http://www.kernel.org/pub/linux/docs/manpages/Archive/": [["man-pages"],[]],
           "http://mirror.sourceshare.org/savannah/man-db/": [["man-db"],[]],
           "http://www.kernel.org/pub/linux/utils/kernel/module-init-tools/": [["module-init-tools"],[]],
           "http://www.kernel.org/pub/linux/utils/kernel/hotplug/": [["udev"],[]],
           "http://ftp.vim.org/pub/vim/unix/": [["vim"],[]]
          }

def get_releases(last_crawl=None):
  pkgs = []
  for source in SOURCES:
    info = helper.open_dir(source)
    if info==None:
      return []
    for d,fn,date in info:
      if not d and (last_crawl==None or date>last_crawl):
        rel = parsers.parse_filename(fn)
        # check version
        for bad_version in SOURCES[source][1]:
          if rel != None and bad_version in rel[2]:
            continue
        if rel != None and rel[0] in SOURCES[source][0]:
          rel[3] = date
          pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs

if __name__=="__main__":
  pkgs = get_releases()
  for p in pkgs:
    print p[0], p[2]
