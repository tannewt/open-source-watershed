# -*- coding: utf-8 -*-
# Create your views here.
import os

from django.http import HttpResponse
from django.shortcuts import render_to_response

from utils.history import PackageHistory
from utils.stats import DataStats, PackageStats
from utils.crawlhistory import CrawlHistory
from utils.search import Search
from utils.errors import *

def index(request):
	s = DataStats()
	upstream = CrawlHistory()
	rest = []
	for distro in ["arch","debian", "fedora", "funtoo", "gentoo", "opensuse", "sabayon", "slackware", "ubuntu"]:
		try:
			ch = CrawlHistory(None,distro)
		except UnknownDistroError:
			continue
		rest.append((distro,ch.today,ch.releases[:5]))
	
	return render_to_response('index.html',
		{"stats": s,
		"crawl_stats":[("Upstream",upstream.today,upstream.releases[:5])]+rest
		}
	)

def distro(request, distro):
	return HttpResponse("Hello, this is the distro page for %s."%(distro,))

STAT_DISTROS = [("arch","current"),("arch","future"),
								("debian","current"),("debian","future"),
								("fedora","current"),("fedora","future"),
								("gentoo","current"),("gentoo","future"),
								("opensuse","current"),("opensuse","future"),("opensuse","experimental"),
								("sabayon","current"),("sabayon","future"),
								("slackware","current"),("slackware","future"),
								("ubuntu","current"),("ubuntu","future")
]
def pkg(request, pkg):
	ps = PackageStats(pkg)
	s = DataStats()
	h = ps.hist.timeline[-5:]
	history = []
	for d in h:
		history.insert(0, (d, h[d]))
	return render_to_response('pkg.html',
		{"stats": s,
		"pkg_stats":filter(lambda x: x!=None, map(lambda x: ps.for_distro(*x),STAT_DISTROS)),
		"name" : pkg,
		"description" : ps.hist.description,
		"history" : history,
		"approx" : ps.hist.ish,
		"True" : True
		}
	)

def search2(request, search):
	search = Search(search)
	s = DataStats()
	
	results = []
	for name,history in search.results:
		line = [name[:20], history.name[:20], history.description, str(history.timeline[-1][1])]
		if history.ish:
			line[-1] += "*"
		if line[0]==line[1]:
			line[1] = "-"
		results.append(line)
	return render_to_response('search2.html',
		{"stats": s,
		"search": search.search,
		"results" : results
		}
	)

def search(request, search):
	search = Search(search, basic=True)
	s = DataStats()
	
	results = []
	for name,description in search.results:
		if len(name)>35:
			name = name[:32]+"..."
		line = [name, description]
		results.append(line)
	return render_to_response('search.html',
		{"stats": s,
		"search": search.search,
		"results" : results
		}
	)

def pkg_set(request, group):
	p = PackageHistory("inkscape")
	s = DataStats()
	return render_to_response('pkg_set.html',
		{"stats": s,
			"name": "package set",
			"set_name": "test set",
			"distros": [],
			"pkg_set": [p]
		}
	)