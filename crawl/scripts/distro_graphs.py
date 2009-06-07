# -*- coding: utf-8 -*-
# Based on age_pic
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

# Get Upstream
def to_history(name):
	try:
		return PackageHistory(name)
	except:
		return None

upstream = filter(lambda x: x != None, map(to_history, upstream))

def to_color(c):
	h = hex(c)[2:]
	return "0"*(4-len(h))+h

distros = []
# get downstream
for d in downstream:
	print d
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
	
	distros.append((key,distro))
	
					# COUNT, BINARY, PREFIX
graphs = [[False, False, "lag_", "Date", "Lag (months)"],
					[True, False, "obsolete_count_", "Date", "Number Obsolete"],
					[True, True, "obsolete_", "Date", "Fraction Obsolete"]]
for COUNT, BINARY, PREFIX, xlabel, ylabel in graphs:
	print PREFIX
	graph = chart.LineChart(select=False,title=title, label_x=xlabel, label_y=ylabel)
	graph.show()
	
	now = datetime.now()
	crawl_start = datetime(2008,10,17)
	pre_crawl_start = datetime(2008,10,16)
	d6m = timedelta(weeks=26)
	d1y = timedelta(weeks=54)
	
	for key,distro in distros:
		branch = distro.branch
		dash = None
		if branch=="future":
			dash = goocanvas.LineDash([2.0,2.0])
		elif branch=="experimental":
			dash = goocanvas.LineDash([2.0,5.0])
		elif branch=="lts":
			dash = goocanvas.LineDash([10.0,2.0])
		elif branch=="past":
			dash = goocanvas.LineDash([10.0,10.0])
		
		if not COUNT:
			notes = []
			if NOTES:
				notes = distro.notes
			graph.add(key,distro.timeline[pre_crawl_start:now],notes,distro.color,dash)
		elif BINARY:
			graph.add(key,distro.bin_obs_timeline[pre_crawl_start:now],[],distro.color,dash)
		else:
			print distro.obs_timeline[pre_crawl_start:now]
			graph.add(key,distro.obs_timeline[pre_crawl_start:now],[],distro.color,dash)
	
	
	graph.set_x_bounds(crawl_start,now)
	if not COUNT:
		graph.set_y_bounds(timedelta(),timedelta(weeks=36))
	elif BINARY:
		graph.set_y_bounds(0.0,1.0)
	
	class bounds:
		width = WIDTH
		height = HEIGHT
		
	graph._resize(None, bounds)
	
	if NOTES:
		graph.toggle_all_notes()
	
	graph._move_points(WIDTH,HEIGHT)
	
	fn = PREFIX + FILENAME
	if FILENAME.endswith(".png"):
		img = cairo.ImageSurface(cairo.FORMAT_ARGB32,WIDTH,HEIGHT)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
		img.write_to_png(fn)
	elif FILENAME.endswith(".svg"):
		img = cairo.SVGSurface(fn,WIDTH,HEIGHT)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif FILENAME.endswith(".eps"):
		img = cairo.PSSurface(fn,WIDTH,HEIGHT)
		img.set_eps(True)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif FILENAME.endswith(".pdf"):
		img = cairo.PDFSurface(fn,WIDTH,HEIGHT)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	else:
		print "not rendered: unknown file extension"