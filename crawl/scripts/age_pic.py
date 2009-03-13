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

DATA = False
if "--data" in sys.argv:
	DATA = True
	sys.argv.remove("--data")

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

class bounds:
	width = 500
	height = 300
	
graph._resize(None, bounds)

if DATA:
	out = open("data.php","w")
	out.write("<?php\n$distro_data = array(\n")

def to_html_color(c):
	return "#"+"".join(map(lambda x: hex(x/256)[2:], c))

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
	
	if DATA:
		out.write("\"%s\" => array(\"color\" => \"%s\", \"name\" => \"%s\", \"age\" => \"%s\", \"pkgs\" => array(\n"%(d,to_html_color(c),name,distro.timeline[-1][1]))
		for pkg in distro._packages:
			package, downstream, age = distro._packages[pkg]
			out.write("  \"%s\" => array(\"upstream\" => \"%s\", \"downstream\" => \"%s\", \"age\" => \"%s\"),\n"%(pkg,package.timeline[-1][1],downstream[-1][1],age[-1][1]))
		out.write(")),\n")
	
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
	
	graph.add(key,distro.timeline,[],"#"+"".join(map(to_color,c)),dash)

if DATA:
	out.write(");\n?>")
	out.close();

now = datetime.now()
d6m = timedelta(weeks=26)

graph.set_x_bounds(now-d6m,now)
graph.set_y_bounds(timedelta(),timedelta(weeks=52))

graph._move_points(500,300)

img = cairo.ImageSurface(cairo.FORMAT_ARGB32,500,300)
context = cairo.Context(img)
graph.render(context,None,1.0)
img.write_to_png("output.png")
