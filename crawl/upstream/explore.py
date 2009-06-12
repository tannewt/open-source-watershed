# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers

NAME="explore"
												#start dir																		 #good pkgs	#bad version parts #target depth #deadends
SOURCES =	{"abiword": ["http://www.abisource.com/downloads/abiword/", ["abiword", "abiword-docs", "abiword-extra", "abiword-plugins"], [], [],								2,						["Windows/", "qnx/", "Fedora/", "MacOSX/", "RedHat/", "Linux/"]],
						"mysql":	 ["http://mirror.services.wisc.edu/mirrors/mysql/Downloads/", ["mysql"], [], ["solaris", "freebsd", "hpux", "osx"], 1, []],
						"ntp":		 ["ftp://ftp.udel.edu/pub/ntp/ntp4/", ["ntp"], [], [], 1, []],
						"ruby":		["ftp://ftp.ruby-lang.org/pub/ruby/", ["ruby"], [], [], 1, []],
						"sane":		["ftp://ftp.sane-project.org/pub/sane/", ["xsane", "sane", "sane-backends", "sane-frontends"], [], [], 2, []],
						"seamonkey":["http://ftp.mozilla.org/pub/mozilla.org/mozilla.org/seamonkey/releases/", ["seamonkey"], [".source"], [], 1, []],
						"util-linux-ng":["http://www.kernel.org/pub/linux/utils/util-linux-ng/", ["util-linux-ng"], [], [], 1, []],
						"util-linux":   ["http://www.kernel.org/pub/linux/utils/util-linux/", ["util-linux"], [], [], 1, []]}

def contains(s, parts):
	for p in parts:
		if p in s:
			return True
	return False

def explore(last_crawl, url, good, fn_remove, badv, depth, dead):
	#print url
	pkgs = []
	info = helper.open_dir(url)
	if info==None:
		return []
	for d,name,date in info:
		if last_crawl!=None and date!=None and depth<2 and date<last_crawl:
			continue
		if d and name not in dead and depth>0:
			if not name.endswith("/"):
				name += "/"
			pkgs += explore(last_crawl, url+name, good, fn_remove, badv, depth-1, dead)
		elif not d:
			for token in fn_remove:
				if token in name:
					name = name.replace(token, "")
			rel = parsers.parse_filename(name)
			if rel!=None and rel[0] in good and not contains(rel[2],badv):
				rel[-2] = date
				#print rel
				pkgs.append(rel)
	return pkgs
	
def get_releases(last_crawl=None):
	rels = []
	for key in SOURCES:
		print "exploring",key
		rels += explore(last_crawl, *SOURCES[key])
	return rels

if __name__=="__main__":
	if len(sys.argv)<2:
		pkgs = get_releases()
	else:
		pkgs = []
		for p in sys.argv[1:]:
			pkgs += explore(None, *SOURCES[p])
	
	for p in pkgs:
		print p[0], p[2], p[3]