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

def _render(graph, fn, prefix, width, height):
	if fn.endswith(".png"):
		img = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
		img.write_to_png(prefix+fn)
	elif fn.endswith(".svg"):
		img = cairo.SVGSurface(prefix+fn,width,height)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif fn.endswith(".eps"):
		img = cairo.PSSurface(prefix+fn,width,height)
		img.set_eps(True)
		context = cairo.Context(img)
		graph.render(context,None,1.0)
	elif fn.endswith(".pdf"):
		img = cairo.PDFSurface(prefix+fn,width,height)
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

def get_lag_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average package lag over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title)
	graph.show()

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
			distro = DistroHistory(name,upstream)
		
		c = distro.color
		
		dash = _get_dash(branch)
		
		timeline = distro.get_lag_timeline()
		print timeline
		graph.add(key,timeline,[],distro.color,dash)


	now = datetime.now()
	if timespan==None:
		crawl_start = start_date
	else:
		crawl_start = now - timespan

	graph.set_x_bounds(crawl_start,now)

	class Bounds:
		pass
	
	bounds = Bounds()
	bounds.width = width
	bounds.height = height
	
	graph._resize(None, bounds)

	graph._move_points(width,height)

	_render(graph, fn, prefix, width, height)
	
	return prefix+fn

def get_obsoletion_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average obsoletion over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title)
	graph.show()

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
			distro = DistroHistory(name,upstream)
		
		c = distro.color
		
		dash = _get_dash(branch)
		
		timeline = distro.get_obsoletion_timeline()
		print timeline
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

	_render(graph, fn, prefix, width, height)
	
	return prefix+fn

def get_obsoletion_count_graph(downstream, upstream, fn="output.png", width=500, height=300, start_date=datetime(2008,10,17), timespan=None, title="Average number of newer releases over time."):
	def to_history(name):
		try:
			return PackageHistory(name)
		except:
			return None

	upstream = filter(lambda x: x != None, map(to_history, upstream))

	graph = chart.LineChart(select=False,title=title)
	graph.show()

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
			distro = DistroHistory(name,upstream)
		
		c = distro.color
		
		dash = _get_dash(branch)
		
		timeline = distro.get_obsoletion_count_timeline()
		print timeline
		graph.add(key,timeline,[],distro.color,dash)


	now = datetime.now()
	if timespan==None:
		crawl_start = start_date
	else:
		crawl_start = now - timespan

	graph.set_x_bounds(crawl_start,now)
	#if not COUNT:
	#	graph.set_y_bounds(timedelta(),timedelta(weeks=36))
	#elif BINARY:
	#	graph.set_y_bounds(0.0,1.0)

	class Bounds:
		pass
	
	bounds = Bounds()
	bounds.width = width
	bounds.height = height
	
	graph._resize(None, bounds)

	graph._move_points(width,height)

	_render(graph, fn, prefix, width, height)
	
	return prefix+fn

if __name__=="__main__":
	print get_lag_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_lag.png")
	print get_obsoletion_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_obs.png")
	print get_obsoletion_count_graph(["gentoo:past"], ["inkscape", "gcc"], fn="output_obs_count.png")