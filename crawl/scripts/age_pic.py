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

COUNT = False
if "--count" in sys.argv:
	COUNT = True
	sys.argv.remove("--count")

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

def to_history(name):
	try:
		return PackageHistory(name)
	except:
		return None

upstream = filter(lambda x: x != None, map(to_history, upstream))

graph = chart.LineChart(select=False,title=title)
graph.show()

def to_str(t):
  if t.days<7:
    return str(t.days)+" days"
  else:
    return str(int(t.days/7))+" weeks"

for d in downstream:
	if d.count(":")==2:
		name, branch, codename = d.split(":")
		key = "_".join((name,branch,codename))
		distro = DistroHistory(name,upstream,branch)
	elif d.count(":")==1:
		name, branch = d.split(":")
		key = "_".join((name,branch))
		distro = DistroHistory(name,upstream,branch)
	else:
		name = d
		distro = DistroHistory(name,upstream,branch)
	
	c = DISTRO_COLORS[name]
	
	dash = None
	if branch=="future":
		dash = goocanvas.LineDash([2.0,2.0])
	elif branch=="experimental":
		dash = goocanvas.LineDash([2.0,5.0])
	elif branch=="lts":
		dash = goocanvas.LineDash([10.0,2.0])
	elif branch=="past":
		dash = goocanvas.LineDash([10.0,10.0])
	
	def to_color(c):
		h = hex(c)[2:]
		return "0"*(4-len(h))+h
	
	if not COUNT:
		notes = []
		if NOTES:
			notes = distro.notes
		graph.add(key,distro.timeline,notes,"#"+"".join(map(to_color,c)),dash)
	else:
		graph.add(key,distro.obs_timeline,[],"#"+"".join(map(to_color,c)),dash)


now = datetime.now()
d6m = timedelta(weeks=26)

graph.set_x_bounds(now-d6m,now)
if not COUNT:
	graph.set_y_bounds(timedelta(),timedelta(weeks=36))

class bounds:
	width = WIDTH
	height = HEIGHT
	
graph._resize(None, bounds)

if NOTES:
  graph.toggle_all_notes()

graph._move_points(WIDTH,HEIGHT)

img = cairo.ImageSurface(cairo.FORMAT_ARGB32,WIDTH,HEIGHT)
context = cairo.Context(img)
graph.render(context,None,1.0)
img.write_to_png(FILENAME)
