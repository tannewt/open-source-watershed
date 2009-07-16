# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from utils import helper
import re
import time
import datetime
from utils.db import upstream
from utils.types import UpstreamRelease
from utils.cache import Cache

NAME = "mysql"
source_id = upstream.source("mysql", "custom mysql crawler")
VERSIONS = ["mysql-5.1","mysql-5.0","mysql-4.1","mysql-6.0"]

def get_date(m_d):
	if m_d.has_key("day") and m_d["day"]:
		if m_d.has_key("smonth") and m_d["smonth"]:
			try:
				return datetime.datetime.strptime(" ".join([m_d["day"],m_d["smonth"],m_d["year"]]),"%d %b %Y")
			except e:
				print "ERROR: parsing date failed: %s"%e
		elif m_d.has_key("month"):
			#special case
			if m_d["month"]=="Sept":
				m_d["month"]="September"
			try:
				return datetime.datetime.strptime(" ".join([m_d["day"],m_d["month"],m_d["year"]]),"%d %B %Y")
			except e:
				print "ERROR: parsing date failed: %s"%e
		else:
			return None
	return None

def get_releases(last_crawl=None):
	pkgs = []
	for ver in VERSIONS:
		filename = "files/mysql/list-" + ver + "-" + str(time.time()) + ".html"
		info = helper.open_url("http://downloads.mysql.com/archives.php?p="+ver+"&o=other",filename,last_crawl)
		if info==None:
			return pkgs
		
		changes = open(filename)
		date = "(?P<day>[0-9][0-9]?) ((?P<smonth>[A-Z][a-z][a-z])|(?P<month>[A-Z][a-z]+)) (?P<year>[0-9]{4})"
		version = "(?P<version>[0-9\.\-a-z]+)"
		bracket_stuff = "( \[.*\])?"
		#									 Version 1.1.3
		line_pattern = re.compile("<a href=\"/archives/%s/mysql-%s\.tar\.gz\"><strong>mysql-[0-9\.\-a-z]+.tar.gz</strong> \(%s, .*\)</a><br />"%(ver,version,date))
		for line in changes:
			line = line.strip("\n")
			m = line_pattern.search(line)
			if m:
				rel = UpstreamRelease()
				rel.package = "mysql"
				m_d = m.groupdict()
				if m_d.has_key("version"):
					rel.version = m_d["version"]
				
				if m_d.has_key("year"):
					rel.released = get_date(m_d)
				if rel.version and rel.released and (last_crawl==None or rel.released>last_crawl):
					pkgs.append(rel)
	return pkgs

def crawl(test):
	print "mysql"
	cache = Cache()
	last_crawl = upstream.last_crawl(source_id)
	rels = get_releases(last_crawl)
	count, max_date = upstream.add_releases(source_id, rels, test, cache)
	print "\t"+str(count),"new releases"
	upstream.set_last_crawl(source_id, max_date, test)

if __name__=="__main__":
	pkgs = get_releases()
	
	for p in pkgs:
		print p