# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers
import httplib
import time
import re
import datetime
import urllib2
from utils.db import sf as sf_module
from utils.db import upstream
from utils.cache import Cache

NAME="sourceforge"

source_id = upstream.source("sf", "generic sourceforge crawler")

def get_files(project_id, paths=["/"], last_crawl=None):
	limit = 10
	if last_crawl==None:
		limit = 100
	
	i = 0
	files = []
	for path in paths:
		fn = "files/sourceforge/%d-%s-%d.rss"%(time.time(),project_id,i)
		try:
			ret = helper.open_url("http://sourceforge.net/api/file/index/project-id/%s/mtime/desc/limit/%d/rss?path=%s"%(project_id,limit,path),fn)
		except httplib.BadStatusLine:
			print "ERROR bad status"
			return []
		except urllib2.URLError:
			print "ERROR UrlError"
			return []
		
		if ret==None:
			print " ERROR"
			return []
		
		pattern_file = re.compile("<link>http://sourceforge.net/projects/.*(?:%2F|/)(\S*)/download</link>")
		pattern_date = re.compile("<pubDate>(.*) [\+-][0-9]{4}</pubDate>")
		
		fs = []
		for line in open(fn):
			tmp_fs = pattern_file.findall(line)
			if len(tmp_fs)>0:
				fs=tmp_fs
			ds = pattern_date.findall(line)
			if len(ds)>0:
				d = datetime.datetime.strptime(ds[0],"%a, %d %b %Y %H:%M:%S")
				for f in fs:
					files.append((f,d))
					fs = []
	i += 1
	return files

def contains(s, parts):
	for p in parts:
		if p in s:
			return True
	return False
	
def get_releases(project_num, packages, bad_tokens, bad_versions, paths, last_crawl):
	rels = []
	
	files = get_files(project_num, paths, last_crawl)
	for f in files:
		if contains(f[0],bad_tokens):
			continue
		rel = parsers.parse_filename(f[0])
		
		if rel!=None and rel.package in packages and not contains(rel.version, bad_versions):
			rel.released = f[1]
			rels.append(rel)
	return rels

def crawl(test=False):
	cache = Cache()
	sources = sf_module.get_sf_targets()
	all_rels = []
	total_new = 0
	for target in sources:
		print target[1]
		rels = get_releases(*target[2:])
		all_rels += rels
		
		count, max_date = sf_module.add_releases(source_id, target[0], rels, test, cache)
		total_new += count
		print "\t"+str(count),"new releases"
		sf_module.set_last_crawl(target[0], max_date, test)
	return (total_new, all_rels)

if __name__=="__main__":
	if len(sys.argv)<2:
		count, pkgs = crawl(True)
	else:
		pkgs = []
		for p in sys.argv[1:]:
			target = sf_module.get_sf_target(p)
			pkgs += get_releases(*target[2:])
	
	for p in pkgs:
		print p
