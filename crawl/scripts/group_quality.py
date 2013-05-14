import sys
import os

sys.path.append(os.getcwd())

from utils import history
from utils.db import groups

if len(sys.argv)<2:
  print sys.argv[0],"<group name>"

if len(sys.argv)>2:
  num_bugs = int(sys.argv[2])
else:
  num_bugs = None

total = 0
fake_upstream = 0
missing_distro = 0

ALL_DISTROS = set(['sabayon', 'fedora', 'gentoo', 'funtoo', 'opensuse', 'slackware', 'arch', 'debian', 'ubuntu'])

BUGS = map(lambda x: [], [0] * 10)

for pkg in groups.get_group(sys.argv[1]):
  total += 1
  pkg = pkg.strip()
  hist = history.PackageHistory(pkg)
  
  bugs = 0
  
  ups = "real"
  if hist.ish:
    ups = "fake"
    fake_upstream += 1
    bugs += 1
  
  missing = []
  if len(hist.aliases)<9:
    missing_distro += 1
    missing = list(ALL_DISTROS - set(hist.aliases.keys()))
    bugs += len(missing)
  
  if num_bugs == None or num_bugs == bugs:
    print pkg, ups, missing
  #BUGS[bugs].append(pkg)
print
print fake_upstream,"/",total,"with approx upstream"
print missing_distro,"/",total,"missing from a distro"
for i in range(10):
  print i, len(BUGS[i])
