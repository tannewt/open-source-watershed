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
import distros.freebsd

import gc
import traceback
import time

import upstream.subversion
import upstream.sf
import upstream.php
import upstream.explore
import upstream.mysql

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
					 "funtoo"		: distros.funtoo,
					 "freebsd"	: distros.freebsd}

UPSTREAM = {"subversion": upstream.subversion,
						"sf"				: upstream.sf,
						"php"				: upstream.php,
						"explore"		: upstream.explore,
						"mysql"			: upstream.mysql}

import utils.helper

import datetime
import time
import sys
import cPickle as pickle

gc.enable()

def crawl(mod):
	cache = Cache()
	repos = mod.get_repos(test)
	i = 0
	for repo in repos:
		print str(i)+"/"+str(len(repos)),repo
		s = time.clock()
		if not last:
			repo.last_crawl = None
		last_crawl, rels = mod.crawl_repo(repo)
		total_new = downstream.add_releases(repo, rels, test, cache)
		if total_new > 0:
			cache.evict([(None, repo.distro_id)])
		downstream.set_last_crawl(repo, last_crawl, test)
		print "\t"+str(total_new),"new releases","\t\t",time.clock()-s,"secs"
		i += 1

if "--ignore-last" in sys.argv:
	sys.argv.remove("--ignore-last")
	last = False
else:
	last = True

if "--test" in sys.argv:
	sys.argv.remove("--test")
	test = True
else:
	test = False

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

total_start = time.clock()
stats = []
for d in downstream_targets:
	s = time.clock()
	try:
		stats.append((d,crawl(DISTROS[d])))
	except:
		print "error from distro:",d
		print traceback.format_exc()
	gc.collect()
	print time.clock() - s, "distro seconds"

for u in upstream_targets:
	s = time.clock()
	try:
		stats.append((u,UPSTREAM[u].crawl(test)))
	except:
		print "error from upstream:",u
		print traceback.format_exc()
	gc.collect()
	print time.clock() - s, "upstream seconds"

cache = Cache()
cache.evict([(None, None)])

print time.clock()-total_start,"seconds total"

save_to = open("/var/www/crawl.oswatershed.org/htdocs/"+str(int(time.time()))+".pickle","w")
pickle.dump(stats,save_to)
save_to.close()
