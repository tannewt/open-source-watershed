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

def _render(graph, fn, width, height):
	if fn.endswith(".png"):
		img = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
		img.write_to_png(fn)
	elif fn.endswith(".svg"):
		img = cairo.SVGSurface(fn,width,height)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif fn.endswith(".eps"):
		img = cairo.PSSurface(fn,width,height)
		img.set_eps(True)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif fn.endswith(".pdf"):
		img = cairo.PDFSurface(fn,width,height)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	else:
		print "not rendered: unknown file extension"

def _get_dash(branch):
	dash = None
	if branch=="future":
		dash = goocanvas.LineDash([2.0,2.0])
	elif branch=="experimental":
		dash = goocanvas.LineDash([2.0,5.0])
	elif branch=="lts":
		dash = goocanvas.LineDash([10.0,2.0])
	elif branch=="past":
		dash = goocanvas.LineDash([10.0,10.0])
	return dash

def _process_distro_tag(d, upstream):
	if d.count(":")==2:
		name, branch, codename = d.split(":")
		key = "_".join((name,branch,codename))
		distro = DistroHistory(name,upstream,branch,now=datetime.now())
	elif d.count(":")==1:
		name, branch = d.split(":")
		key = "_".join((name,branch))
		distro = DistroHistory(name,upstream,branch,now=datetime.now())
	else:
		name = d
		distro = DistroHistory(name,upstream,now=datetime.now())
	return (distro, branch, key)

def get_lag_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average package lag over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title, label_x='Date', label_y='Average Lag')
	graph.show()
	
	now = datetime.now()
	if timespan==None:
		crawl_start = start_date
	else:
		crawl_start = now - timespan
	
	max_y = timedelta()
	for d in downstream:
		distro, branch, key = _process_distro_tag(d, upstream)
		
		dash = _get_dash(branch)
		
		timeline = distro.get_lag_timeline()
		m = max(timeline[crawl_start:now].values())
		if max_y < m:
			max_y = m
		graph.add(key,timeline,[],distro.color,dash)
	
	graph.set_x_bounds(crawl_start,now)
	graph.set_y_bounds(timedelta(),max_y)

	class Bounds:
		pass
	
	bounds = Bounds()
	bounds.width = width
	bounds.height = height
	
	graph._resize(None, bounds)

	graph._move_points(width,height)

	_render(graph, fn, width, height)
	
	return fn

def get_obsoletion_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average obsoletion over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title, label_x='Date', label_y='Fraction Obsolete')
	graph.show()

	for d in downstream:
		distro, branch, key = _process_distro_tag(d, upstream)
		
		dash = _get_dash(branch)
		
		timeline = distro.get_obsoletion_timeline()
		graph.add(key,timeline,[],distro.color,dash)


	now = datetime.now()
	if timespan==None:
		crawl_start = start_date
	else:
		crawl_start = now - timespan

	graph.set_x_bounds(crawl_start,now)
	graph.set_y_bounds(0.0,1.0)

	class Bounds:
		pass
	
	bounds = Bounds()
	bounds.width = width
	bounds.height = height
	
	graph._resize(None, bounds)

	graph._move_points(width,height)

	_render(graph, fn, width, height)
	
	return fn

def get_obsoletion_count_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average number of newer releases over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title, label_x='Date', label_y='Average Number of New Releases')
	graph.show()
	
	now = datetime.now()
	if timespan==None:
		crawl_start = start_date
	else:
		crawl_start = now - timespan
	
	max_y = 0.0
	for d in downstream:
		distro, branch, key = _process_distro_tag(d, upstream)
		
		dash = _get_dash(branch)
		
		timeline = distro.get_obsoletion_count_timeline()
		m = max(timeline[crawl_start:now].values())
		if max_y < m:
			max_y = m
		graph.add(key,timeline,[],distro.color,dash)
	
	graph.set_x_bounds(crawl_start,now)
	graph.set_y_bounds(0.0,max_y)

	class Bounds:
		pass
	
	bounds = Bounds()
	bounds.width = width
	bounds.height = height
	
	graph._resize(None, bounds)

	graph._move_points(width,height)

	_render(graph, fn, width, height)
	
	return fn

if __name__=="__main__":
	print get_lag_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_lag.png")
	print get_obsoletion_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_obs.png")
	print get_obsoletion_count_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_obs_count.png")