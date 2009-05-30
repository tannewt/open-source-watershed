# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.getcwd())
import datetime
import cairo

from utils import history
from utils import chart
from utils.timeline import DayTimeline

FILENAME = sys.argv[-1]
del sys.argv[-1]

FILES=False
if "-f" in sys.argv:
	FILES = True
	sys.argv.remove("-f")

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

if len(sys.argv)>1:
	upstream = []
	if FILES:
		for fn in sys.argv[1:]:
			f = open(fn)
			for p in f:
				print p.strip()
				upstream.append(history.PackageHistory(p.strip()))
			f.close()
	else:
		for p in sys.argv[1:]:
			upstream.append(history.PackageHistory(p))
else:
	upstream = history.get_upstream()

cumulativeTimeline = DayTimeline(default=[])
for hist in upstream:
	cumulativeTimeline = cumulativeTimeline + hist.count

now = datetime.datetime.now()
crawl_start = datetime.datetime(2008,10,17)
d6m = datetime.timedelta(weeks=26)
d1y = datetime.timedelta(weeks=54)
cumulativeTimeline = cumulativeTimeline[crawl_start:now]
print cumulativeTimeline
countTimeline = DayTimeline()
for key in cumulativeTimeline:
	countTimeline[key] = len(cumulativeTimeline[key])

graph = chart.BarChart(countTimeline, label_x="Date", label_y="Releases")
graph.show()

graph.set_x_bounds(crawl_start,now)

class bounds:
	width = WIDTH
	height = HEIGHT
	
graph._resize(None, bounds)

if NOTES:
  graph.toggle_all_notes()

#graph._move_points(WIDTH,HEIGHT)

if FILENAME.endswith(".png"):
	img = cairo.ImageSurface(cairo.FORMAT_ARGB32,WIDTH,HEIGHT)
	context = cairo.Context(img)
	graph.render(context,None,1.0)
	img.write_to_png(FILENAME)
elif FILENAME.endswith(".svg"):
	img = cairo.SVGSurface(FILENAME,WIDTH,HEIGHT)
	context = cairo.Context(img)
	graph.render(context,None,1.0)
elif FILENAME.endswith(".eps"):
	img = cairo.PSSurface(FILENAME,WIDTH,HEIGHT)
	img.set_eps(True)
	context = cairo.Context(img)
	graph.render(context,None,1.0)
elif FILENAME.endswith(".pdf"):
	img = cairo.PDFSurface(FILENAME,WIDTH,HEIGHT)
	context = cairo.Context(img)
	graph.render(context,None,1.0)
else:
	print "not rendered: unknown file extension"