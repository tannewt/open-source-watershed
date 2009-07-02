# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers
from utils.db import explore as explore_module
from utils.db import upstream

NAME="explore"
source_id = upstream.source("explore", "generic directory crawler")

def contains(s, parts):
	for p in parts:
		if p in s:
			return True
	return False

def explore(url, depth, good, bad, fn_remove, badv, dead, last_crawl):
	#print url
	pkgs = []
	info = helper.open_dir(url)
	
	if depth!=None and depth>0:
		new_depth = depth - 1
	elif depth==None:
		new_depth = None
	
	if info==None:
		return []
	for d,name,date in info:
		if last_crawl!=None and date!=None and depth<2 and date<last_crawl:
			continue
		
		if d and name not in dead and (depth==None or depth>0):
			if not name.endswith("/"):
				name += "/"
			
			pkgs += explore(url+name, new_depth, good, bad, fn_remove, badv, dead, last_crawl)
		elif not d:
			for token in fn_remove:
				if token in name:
					name = name.replace(token, "")
			rel = parsers.parse_filename(name)
			
			if rel!=None and ((good != None and rel.package in good and bad==None) or (good == None and bad != None and rel.package not in bad)) and not contains(rel.version, badv):
				rel.released = date
				#print "*",rel
				pkgs.append(rel)
			elif rel != None:
				#print rel
				pass
	return pkgs
	
def crawl():
	sources = explore_module.get_explore_targets()
	for target in sources:
		print target[1]
		rels = explore(*target[2:])
		count, max_date = explore_module.add_releases(source_id, target[0], rels)
		print "\t"+str(count),"new releases"
		explore_module.set_last_crawl(target[0], max_date)

if __name__=="__main__":
	if len(sys.argv)<2:
		pkgs = get_releases()
	else:
		pkgs = []
		for p in sys.argv[1:]:
			target = explore_module.get_explore_target(p)
			pkgs += explore(*target[2:])
	
	for p in pkgs:
		print p