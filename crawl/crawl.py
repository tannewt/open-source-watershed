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
import upstream.single_dir
import upstream.php
import upstream.explore

from utils.cache import Cache

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
						"single_dir": upstream.single_dir,
						"php"				: upstream.php,
						"explore"		: upstream.explore}

import utils.helper

import datetime
import time
import sys
import cPickle as pickle

gc.enable()
stats = []

if "--ignore-last" in sys.argv:
	sys.argv.remove("--ignore-last")
	last = False
else:
	last = True

if len(sys.argv)>1:
	if "upstream" in sys.argv:
		sys.argv.remove("upstream")
		for u in UPSTREAM.keys():
			try:
				stats.append((u,UPSTREAM[u].crawl()))
			except:
				print "error from upstream:",u
				print traceback.format_exc()
			gc.collect()
	if "downstream" in sys.argv:
		sys.argv.remove("downstream")
		for d in DISTROS.keys():
			try:
				stats.append((d,DISTROS[d].crawl()))
			except:
				print "error from upstream:",d
				print traceback.format_exc()
			gc.collect()
	for crawl in sys.argv[1:]:
		if DISTROS.has_key(crawl):
			try:
				stats.append((crawl,DISTROS[crawl].crawl()))
			except:
				print "error from distro:",crawl
				print traceback.format_exc()
			gc.collect()
			continue
		if UPSTREAM.has_key(crawl):
			try:
				UPSTREAM[crawl].crawl()
			except:
				print "error from upstream:",crawl
				print traceback.format_exc()
			gc.collect()
			continue
		print "unknown",crawl
else:
	print "no args - running all"
	for d in DISTROS.keys():
		try:
			stats.append((d,DISTROS[d].crawl()))
		except:
			print "error from distro:",d
			print traceback.format_exc()
		gc.collect()
	for u in UPSTREAM.keys():
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
