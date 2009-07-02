# -*- coding: utf-8 -*-
import distros.debian
import distros.slackware
import distros.ubuntu
import distros.fedora
import distros.gentoo
import distros.opensuse
import distros.arch
import distros.sabayon
import distros.funtoo

import gc
import traceback

import upstream.subversion
import upstream.sf
import upstream.php
import upstream.explore

from utils.cache import Cache
from utils.db import downstream

DISTROS = {"slackware": distros.slackware,
					 "debian"		: distros.debian,
					 "ubuntu"		: distros.ubuntu,
					 "fedora"		: distros.fedora,
					 "gentoo"		: distros.gentoo,
					 "opensuse"	: distros.opensuse,
					 "arch"			: distros.arch,
					 "sabayon"	: distros.sabayon,
					 "funtoo"		: distros.funtoo}

UPSTREAM = {"subversion": upstream.subversion,
						"sf"				: upstream.sf,
						"php"				: upstream.php,
						"explore"		: upstream.explore}

import utils.helper

import datetime
import time
import sys
import cPickle as pickle

gc.enable()

def crawl(mod):
	repos = mod.get_repos()
	i = 0
	for repo in repos:
		print str(i)+"/"+str(len(repos)),repo
		if not last:
			repo.last_crawl = None
		last_crawl, rels = mod.crawl_repo(repo)
		total_new = downstream.add_releases(repo, rels)
		print "\t"+str(total_new),"new releases"
		downstream.set_last_crawl(repo, last_crawl)
		i += 1

if "--ignore-last" in sys.argv:
	sys.argv.remove("--ignore-last")
	last = False
else:
	last = True

downstream_targets = []
upstream_targets = []
if len(sys.argv)>1:
	if "upstream" in sys.argv:
		sys.argv.remove("upstream")
		upstream_targets = UPSTREAM.keys()
	if "downstream" in sys.argv:
		sys.argv.remove("downstream")
		downstream_targets = DISTROS.keys()
	for t in sys.argv[1:]:
		if DISTROS.has_key(t):
			downstream_targets.append(t)
			continue
		if UPSTREAM.has_key(t):
			upstream_targets.append(t)
			continue
		print "unknown",t
else:
	print "no args - running all"
	upstream_targets = UPSTREAM.keys()
	downstream_targets = DISTROS.keys()

stats = []
for d in downstream_targets:
	try:
		stats.append((d,crawl(DISTROS[d])))
	except:
		print "error from distro:",d
		print traceback.format_exc()
	gc.collect()

for u in upstream_targets:
	try:
		stats.append((u,UPSTREAM[u].crawl()))
	except:
		print "error from upstream:",u
		print traceback.format_exc()
	gc.collect()

cache = Cache()
cache.evict([(None, None)])

save_to = open("crawl_stats/"+str(int(time.time()))+".pickle","w")
pickle.dump(stats,save_to)
save_to.close()
