from utils.helper import *
import re

NAME = "postfix"

def get_releases(last_crawl=None):
  files = open_dir("http://www.tigertech.net/mirrors/postfix-release/official/")
  pattern_patch = re.compile("postfix-([0-9])\.([0-9])-patch([0-9][0-9]).gz")
  pattern_regular = re.compile("postfix-([0-9])\.([0-9]).([0-9][0-9]?).tar.gz")
  pattern_date = re.compile("postfix-([0-9]*)-patch([0-9][0-9]).gz")
  patterns = (pattern_patch, pattern_regular, pattern_date)
  releases = []
  for d,name,modified in files:
    which, match = find_match(name,patterns)
    if match:
      if which == 3:
        epoch = -1
      else:
        epoch = 0
      
      version = ".".join(map(lambda x: str(int(x)),match.groups()))
      releases.append(("postfix", epoch, version, modified, None))
  return releases
