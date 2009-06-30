# -*- coding: utf-8 -*-
import sys
import os
from ConfigParser import ConfigParser

if len(sys.argv)<2:
	print sys.argv[0],"[directories]"

popcon = {}
pkgs = []
config = ConfigParser()
for d in sys.argv[1:]:
	files = os.listdir(d)
	files = filter(lambda x: x.endswith(".desktop"), files)
	for f in files:
		try:
			config.read([d+f])
		except:
			#print "error", f
			pass
		name = config.get("Desktop Entry", "X-AppInstall-Package")
		pop = config.get("Desktop Entry", "X-AppInstall-Popcon")
		popcon[name] = int(pop)
		sec = config.get("Desktop Entry", "X-AppInstall-Section")
		cat = config.get("Desktop Entry", "Categories")
		if sec=="main" and name not in pkgs:
			#print name, pop, sec, cat
			pkgs.append(name)

def pkg_compare(p1, p2):
	return popcon[p2] - popcon[p1]

pkgs = sorted(pkgs, pkg_compare)
for p in pkgs:
	print p