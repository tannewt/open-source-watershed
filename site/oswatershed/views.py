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
from utils.timeline import Timeline

def sidebar():
	upstream = CrawlHistory()
	rest = []
	for distro in ["arch","debian", "fedora", "freebsd", "funtoo", "gentoo", "opensuse", "sabayon", "slackware", "ubuntu"]:
		try:
			ch = CrawlHistory(None,distro)
		except UnknownDistroError:
			continue
		rest.append((distro,ch.today,ch.releases[:5]))
	
	sidebar = [("Released Today:","",""),("Upstream",upstream.today,upstream.releases[:5])]+rest
	return sidebar

def index(request):
	vals = {}
	vals["stats"] = DataStats()
	vals["user"] = maybe_login(request)
	print vals['user']
	if not vals['user'] == None:
		return home(request, vals['user'])
	
	current = DistroRanks()
	future = DistroRanks("future")
	
	vals["crawl_stats"] = sidebar()
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
	if request.session.has_key('user') and request.session['user'].username != None:
		return request.session['user']
	elif user != None:
		request.session['user'] = user
	return user

def home(request, user):
	vals = {}
	vals['user'] = user
	vals['stats'] = DataStats()
	vals["crawl_stats"] = sidebar()
	
	now = datetime.datetime.now()
	week_ago = now - datetime.timedelta(days=7)
	
	timeline = Timeline()
	group = groups.get_group(".tracked")
	print group
	histories = []
	for pkg in group:
		hist = PackageHistory(pkg)
		histories.append(hist)
		for date in hist.timeline[week_ago:]:
			timeline[date] = (None, pkg, hist.timeline[date])
	
	distro = DistroHistory('gentoo', histories)
	for p in group:
		downstream = distro.get_pkg(p)[week_ago:]
		for date in downstream:
			timeline[date] = (distro.name, date.time(), pkg, downstream[date])
	
	feed = [["Today",[]], ["Yesterday",[]]]
	for i in range(2,7):
		day = now - datetime.timedelta(i)
		feed.append([day.strftime("%A"), []])
	
	for date in timeline:
		feed[(now.date() - date.date()).days][1].append(timeline[date])
	print feed
	map(lambda x: x[1].reverse(), feed)
	
	vals["release_feed"] = feed
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

def track_package(request, pkg):
	action = request.GET["action"]
	cb = request.GET["cb"]
	user = maybe_login(request)
	status = "no_user"
	if user != None:
		if action == "track":
			if not groups.has_group(".tracked", user.id):
				groups.create_group(".tracked", user.id)
			groups.add_to_group(pkg, ".tracked", user.id)
			status = "tracked"
		elif action == "untrack":
			if groups.has_group(".tracked", user.id):
				groups.remove_from_group(pkg, ".tracked", user.id)
			status = "untracked"
		elif action == "is_tracked":
			if groups.in_group(pkg, ".tracked", user.id):
				status = "tracked"
			else:
				status = "untracked"
		else:
			status = "unknown_command"
	response = cb + '({"status":"%s"'%(status) + "})"
	return HttpResponse(response)

def api(request, version):
	print request, version