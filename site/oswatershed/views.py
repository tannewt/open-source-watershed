# -*- coding: utf-8 -*-
# Create your views here.
import os
import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response

from utils.history import PackageHistory, DistroHistory
from utils.stats import DataStats, PackageStats, DistroRanks
from utils.crawlhistory import CrawlHistory
from utils.search import Search
from utils.errors import *
from utils.db import groups,users

def index(request):
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	print vals['user']
	upstream = CrawlHistory()
	rest = []
	for distro in ["arch","debian", "fedora", "freebsd", "funtoo", "gentoo", "opensuse", "sabayon", "slackware", "ubuntu"]:
		try:
			ch = CrawlHistory(None,distro)
		except UnknownDistroError:
			continue
		rest.append((distro,ch.today,ch.releases[:5]))
	
	current = DistroRanks()
	future = DistroRanks("future")
	
	sidebar = [("Released Today:","",""),("Upstream",upstream.today,upstream.releases[:5])]+rest
	
	vals["crawl_stats"] = sidebar
	vals["current_distros"] = current.distros
	vals["future_distros"] = future.distros
	vals["True"] = True
	return render_to_response('index.html', vals)

def maybe_login(request):
	user = None
	if request.POST.has_key("username") and request.POST.has_key("password"):
		user = users.get(request.POST["username"], request.POST["password"])
	if (request.GET.has_key("logout") or request.POST.has_key("logout")) and request.session.has_key('user'):
		del request.session['user']
	if request.session.has_key('user'):
		return request.session['user']
	elif user != None:
		request.session['user'] = user
	return user

def home(request):
	vals = {}
	vals['stats'] = DataStats()
	if maybe_login(request):
		pass
	return render_to_response('home.html', vals)

STAT_DISTROS = [("arch","current"),("arch","future"),
								("debian","current"),("debian","future"),("debian","experimental"),
								("fedora","current"),("fedora","future"),
								("freebsd","current"),("freebsd","future"),
								("gentoo","current"),("gentoo","future"),
								("opensuse","current"),("opensuse","future"),
								("sabayon","current"),("sabayon","future"),
								("slackware","current"),("slackware","future"),
								("ubuntu","current"),("ubuntu","future")
]
def pkg(request, pkg):
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	vals["name"] = pkg
	try:
		ps = PackageStats(pkg)
	except UnknownPackageError:
		return render_to_response('unknown_pkg.html', vals)
	h = ps.hist.timeline[-10:]
	history = []
	for d in h:
		history.insert(0, (d, h[d]))
	vals["pkg_stats"] = filter(lambda x: x!=None, map(lambda x: ps.for_distro(*x),STAT_DISTROS))
	vals["description"] = ps.hist.description
	vals["history"] = history
	vals["approx"] = ps.hist.ish
	vals["True"] = True
	return render_to_response('pkg.html', vals)

def search2(request, search):
	search = Search(search)
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	
	results = []
	for name,history in search.results:
		line = [name[:20], history.name[:20], history.description, str(history.timeline[-1][1])]
		if history.ish:
			line[-1] += "*"
		if line[0]==line[1]:
			line[1] = "-"
		results.append(line)
	vals["results"] = results
	vals["search"] = search.search
	return render_to_response('search2.html', vals)

def search(request, search):
	search = Search(search, basic=True)
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	
	results = []
	for name,description in search.results:
		if len(name)>35:
			name = name[:32]+"..."
		line = [name, description]
		results.append(line)
	vals["results"] = results
	vals["search"] = search.search
	return render_to_response('search.html', vals)

def pkg_set(request, group):
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	vals["pkg_set"] = [PackageHistory("inkscape")]
	vals["distros"] = []
	vals["set_name"] = "test set"
	vals["name"] = "package set"
	return render_to_response('pkg_set.html', vals)

def distro(request, distro):
	packages = map(PackageHistory, groups.get_group("twenty"))
	now = datetime.datetime.now()
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	vals["True"] = True
	vals["zero"] = 0
	vals["name"] = distro
	data = []
	for branch in ["future", "current", "past"]:
		try:
			h = DistroHistory(distro, packages, branch, now=now)
		except UnknownDistroError:
			return render_to_response('unknown_distro.html',
				{"stats": s,
				"name" : distro
				}
			)
		if h.codename == None:
			h.codename = ""
		data.append((branch.capitalize(), h.codename.capitalize(), h.snapshot_all_metrics()))
	vals["data"] = data
	return render_to_response('distro.html', vals)