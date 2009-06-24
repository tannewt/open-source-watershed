# -*- coding: utf-8 -*-
from .utils import helper
from .utils import parsers
from .utils.db import core
from .utils.db import upstream

source_id = upstream.source("linux","")

MIRROR="http://www.kernel.org/pub/linux/kernel/"
def crawl():
	count = 0
	rels = []
	last_crawl = upstream.last_crawl(source_id)
	new_last_crawl = last_crawl
	info = helper.open_dir(MIRROR)
	if info==None:
		return []
	for d,name,date in info:
		if d and name[0]=="v" and (last_crawl==None or date>last_crawl):
			p_info = helper.open_dir(MIRROR+name)
			if p_info == None:
				continue
			for d2,n2,date2 in p_info:
				if not d2 and (last_crawl==None or date2>last_crawl):
					rel = parsers.parse_filename(n2)
					if rel != None and rel.package == "linux":
						rel.released = date2
						rels.append(rel)
						if new_last_crawl==None or date2 > new_last_crawl:
							new_last_crawl = date2
	
	upstream.add_releases(source_id, rels)
	
	upstream.set_last_crawl(source_id, new_last_crawl)
	
	#name, epoch, version, date, extra
	#rel = ["subversion",0, None, None, None]

	return count
