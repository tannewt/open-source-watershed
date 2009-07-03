# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers
import time
import re
import datetime
from utils.db import sf as sf_module
from utils.db import upstream

NAME="sourceforge"

source_id = upstream.source("sf", "generic sourceforge crawler")

def get_files(project_id,last_crawl=None):
	limit = 10
	if last_crawl==None:
		limit = 100
	
	fn = "files/sourceforge/%d-%s.rss"%(time.time(),project_id)
	helper.open_url("http://sourceforge.net/export/rss2_projfiles.php?group_id=%s&rss_limit=%s"%(project_id,limit),fn)
	
	pattern_file = re.compile("(\S*) \([0-9]* bytes, [0-9]* downloads to date\)")
	pattern_date = re.compile("<pubDate>(.*)</pubDate>")
	
	files = []
	fs = []
	for line in open(fn):
		tmp_fs = pattern_file.findall(line)
		if len(tmp_fs)>0:
			fs=tmp_fs
		ds = pattern_date.findall(line)
		if len(ds)>0:
			d = datetime.datetime.strptime(ds[0],"%a, %d %b %Y %H:%M:%S %Z")
			for f in fs:
				files.append((f,d))
				fs = []
	return files

def contains(s, parts):
	for p in parts:
		if p in s:
			return True
	return False
	
def get_releases(project_num, packages, bad_tokens, bad_versions, last_crawl):
	rels = []
	
	files = get_files(project_num, last_crawl)
	for f in files:
		if contains(f[0],bad_tokens):
			continue
		rel = parsers.parse_filename(f[0])
		
		if rel!=None and rel.package in packages and not contains(rel.version, bad_versions):
			rel.released = f[1]
			rels.append(rel)
	return rels

def crawl(test=False):
	sources = sf_module.get_sf_targets()
	all_rels = []
	total_new = 0
	for target in sources:
		print target[1]
		rels = get_releases(*target[2:])
		all_rels += rels
		
		count, max_date = sf_module.add_releases(source_id, target[0], rels, test)
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