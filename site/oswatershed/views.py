# -*- coding: utf-8 -*-
# Create your views here.
import os
import datetime

from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.shortcuts import render_to_response

from utils.history import PackageHistory, DistroHistory
from utils.stats import DataStats, PackageStats, DistroRanks
from utils.crawlhistory import CrawlHistory
from utils.search import Search
from utils.errors import *
from utils.db import core
from utils.db import groups

def index(request):
	s = DataStats()
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
	
	return render_to_response('index.html',
		{"stats": s,
		"crawl_stats":sidebar,
		"current_distros":current.distros,
		"future_distros":future.distros,
		"True" : True
		}
	)

def distro(request, distro):
	return HttpResponse("Hello, this is the distro page for %s."%(distro,))

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
	s = DataStats()
	try:
		ps = PackageStats(pkg)
	except UnknownPackageError:
		return render_to_response('unknown_pkg.html',
		{"stats": s,
		 "name" : pkg
		}
	)
	h = ps.hist.timeline[-10:]
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

def distro(request, distro):
	packages = map(PackageHistory, groups.get_group("twenty"))
	now = datetime.datetime.now()
	s = DataStats()
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
	return render_to_response('distro.html',
		{"stats": s,
			"name": distro,
			"data": data,
			"True": True,
			"zero": 0
		}
	)

def sitemap(request, sm):
	s = DataStats()
	pkgs_per_sitemap = 10000
	response = []
	if sm == "index":
	  response.append('<?xml version="1.0" encoding="UTF-8"?>')
	  response.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
	  for i in xrange(0, (s.package_count / pkgs_per_sitemap) + 1):
	    response.append('<sitemap><loc>http://oswatershed.org/sitemap_%d.xml</loc></sitemap>' % i)
	  response.append('</sitemapindex>')
	else:
	  try:
	    sm_index = int(sm)
	  except:
	    return HttpResponse(status=404)
	  if sm_index > s.package_count / pkgs_per_sitemap:
	    return HttpResponse(status=404)
	  response.append('<?xml version="1.0" encoding="UTF-8"?>')
	  response.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
	  response.append('<!-- test -->')
	  if sm_index == 0:
	    response.append('<url><loc>http://oswatershed.org</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
	    ds = core.get_all_distros()
	    for d in ds:
	      response.append('<url><loc>http://oswatershed.org/distro/%s</loc><changefreq>daily</changefreq><priority>0.8</priority></url>' % d)
	  ps = core.get_all_package_names(pkgs_per_sitemap, sm_index * pkgs_per_sitemap)
	  for p in ps:
	    response.append('<url><loc>http://oswatershed.org/pkg/%s</loc></url>' % p)
	  response.append('</urlset>')
	response = "".join(response)
	r = HttpResponse(response)
	r["Content-Length"] = len(response)
	return r

def robots(request):
	return HttpResponse("Sitemap: http://oswatershed.org/sitemap_index.xml")

class PackageFeed(Feed):
    author_name = "Open Source Watershed"
    author_email = "oswatershed@googlegroups.com"
    author_link = "http://oswatershed.org"
    def get_object(self, request, pkg):
        return PackageHistory(pkg)

    def title(self, obj):
        return "OSWatershed: %s" % obj.name

    def link(self, obj):
        return "http://oswatershed.org/pkg/%s" % obj.name

    def feed_url(self, obj):
        return "http://oswatershed.org/pkg/%s/rss.xml" % obj.name

    def description(self, obj):
        if obj.ish:
	    return "Approximate release history of %s" % obj.name
	else:
	    return "Release history of %s" % obj.name

    def categories(self, obj):
        cats = ['linux', 'software', 'oswatershed', obj.name]
	if not obj.ish:
	    cats.append('upstream')
	return cats

    def items(self, obj):
        items = []
        for date in obj.timeline:
	  items.append((date, obj.name, obj.timeline[date]))
	items.reverse()
        return items

    def item_link(self, item):
        return "http://oswatershed.org/pkg/%s" % item[1]

    def item_pubdate(self, item):
        return item[0]

    def item_title(self, item):
        return item[2]

    def item_description(self, item):
        return "%s - %s %s" % item

    def item_guid(self, item):
        return " ".join(item[1:])
