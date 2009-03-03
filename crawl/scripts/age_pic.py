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

print "upstream",upstream
print "downstream",downstream

upstream = map(PackageHistory, upstream)

graph = chart.LineChart(select=False)
graph.show()

class bounds:
	width = 500
	height = 300
	
graph._resize(None, bounds)

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
	graph.add(key,distro.timeline,[],c.to_string(),dash)

now = datetime.now()
d6m = timedelta(weeks=26)

graph.set_x_bounds(now-d6m,now)
graph.set_y_bounds(timedelta(),timedelta(weeks=52))

graph._move_points(500,300)

img = cairo.ImageSurface(cairo.FORMAT_ARGB32,500,300)
context = cairo.Context(img)
graph.render(context,None,1.0)
img.write_to_png("output.png")
