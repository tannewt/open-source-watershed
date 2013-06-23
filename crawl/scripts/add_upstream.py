#!/usr/bin/python2
import os
import sys

sys.path.append(os.getcwd())
from utils.db.explore import *
from upstream import explore
from utils.db.sf import *
from upstream import sf

if len(sys.argv) < 2:
  print sys.argv[0] + " (explore|sf) (add|test|list) (<name> <url> <depth>|<name> <project_num>)"
  sys.exit(1)

t, cmd = sys.argv[1:3]

if t == "explore":
  if cmd == "list":
    print "".join([str(x) + "\n" for x in get_explore_targets()])
  else:
    name, url, depth = sys.argv[3:6]
    depth = int(depth)
    if len(sys.argv) < 7:
      good = [name]
    else:
      good = sys.argv[6:]
    if cmd == "add":
      print "Added:", add_explore_target(name, url, depth, good, None, [], [], []) 
    elif cmd == "test":
      print "".join([str(x) + "\n" for x in explore.explore(url, depth, good, None, [], [], [], None)])
elif t == "sf":
  if cmd == "list":
    print "".join([str(x) + "\n" for x in get_sf_targets()])
  else:
    name, project_num = sys.argv[3:5]
    if cmd == "add":
      print "Added:", add_sf_target(name, project_num, [name], [], [], ['/'])
    elif cmd == "test":
      print "".join([str(x) + "\n" for x in sf.get_releases(project_num, [name], [], [], ['/'], None)])
