# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.getcwd())
import cairo
try:
	import goocanvas
except:
	print "ack headless"
	import utils.headless as goocanvas
from datetime import timedelta, datetime

from utils import chart
from utils import render
from utils.history import *
from age_v_time import DISTRO_COLORS

upstream = []
downstream = []

FILENAME = sys.argv[-1]
del sys.argv[-1]

NOTES = False
if "--notes" in sys.argv:
	NOTES = True
	sys.argv.remove("--notes")

ALL = False
if "--all" in sys.argv:
	ALL = True
	sys.argv.remove("--all")

COUNT = False
if "--count" in sys.argv:
	COUNT = True
	sys.argv.remove("--count")

BINARY = False
if "--binary" in sys.argv:
	BINARY = True
	sys.argv.remove("--binary")

WIDTH = 500
if "--width" in sys.argv:
  i = sys.argv.index("--width")
  del sys.argv[i]
  WIDTH = int(sys.argv.pop(i))

HEIGHT = 300
if "--height" in sys.argv:
  i = sys.argv.index("--height")
  del sys.argv[i]
  HEIGHT = int(sys.argv.pop(i))

if "--uf" in sys.argv[1:]:
	for i in range(sys.argv.index("--uf")+1,len(sys.argv)):
		if not sys.argv[i].startswith("--"):
			f = open(sys.argv[i])
			for line in f:
				if line[0]!="#":
					upstream.append(line.strip())
			f.close()
		else:
			break

if "--df" in sys.argv[1:]:
	pass

if "--u" in sys.argv[1:]:
	for i in range(sys.argv.index("--u")+1,len(sys.argv)):
		if not sys.argv[i].startswith("--"):
			upstream.append(sys.argv[i])
		else:
			break

if "--d" in sys.argv[1:]:
	for i in range(sys.argv.index("--d")+1,len(sys.argv)):
		if not sys.argv[i].startswith("--"):
			downstream.append(sys.argv[i])
		else:
			break

title = ""
if "--t" in sys.argv[1:]:
	title = []
	for i in range(sys.argv.index("--t")+1,len(sys.argv)):
		if not sys.argv[i].startswith("--"):
			title.append(sys.argv[i])
		else:
			break
	title = " ".join(title)

print "upstream",upstream
print "downstream",downstream

if COUNT:
	render.get_obsoletion_count_graph(downstream, upstream, fn=FILENAME, width=WIDTH, height=HEIGHT, title=title)
elif BINARY:
	render.get_obsoletion_graph(downstream, upstream, fn=FILENAME, width=WIDTH, height=HEIGHT, title=title)
elif ALL:
	fn_start, fn_end = FILENAME.rsplit(".", 1)
	render.get_obsoletion_count_graph(downstream, upstream, fn=fn_start+"_count."+fn_end, width=WIDTH, height=HEIGHT, title=title)
	render.get_obsoletion_graph(downstream, upstream, fn=fn_start+"_obs."+fn_end, width=WIDTH, height=HEIGHT, title=title)
	render.get_lag_graph(downstream, upstream, fn=fn_start+"_lag."+fn_end, width=WIDTH, height=HEIGHT, title=title)
else:
	render.get_lag_graph(downstream, upstream, fn=FILENAME, width=WIDTH, height=HEIGHT, title=title)