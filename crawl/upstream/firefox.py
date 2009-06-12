# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers

NAME="firefox"

MIRROR="http://ftp.mozilla.org/pub/mozilla.org/mozilla.org/firefox/releases/"
IGNORE = ["0.8/", "0.9.1/", "0.9.2/", "0.9.3/", "0.9/", "0.9rc", "0.10.1/", "0.10/", "0.10rc/", "1.0.1/"]
def get_releases(last_crawl=None):
	pkgs = []
	list = helper.open_dir(MIRROR)
	for d,name,date in list:
		if name in IGNORE:
			continue
		list2 = helper.open_dir(MIRROR + name + "/source")
		if list2!=None:
			list2 = filter(lambda x: x[1].endswith(".tar.bz2"), list2)
			for d2, fn, date2 in list2:
				fn = fn.replace("-source","")
				rel = parsers.parse_filename(fn)
				if rel != None:
					rel[3] = date2
					pkgs.append(rel)
	return pkgs

if __name__=="__main__":
	pkgs = get_releases()
	for p in pkgs:
		print p[0], p[2]