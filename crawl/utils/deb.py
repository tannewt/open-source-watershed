# -*- coding: utf-8 -*-
import bz2
import gzip
import helper
from utils.types import DownstreamRelease

def parse_packages(parse_version, filename, url, repo):
	rels = []

	last_modified = helper.open_url(url, filename, repo.last_crawl)

	if last_modified==None:
		return (repo.last_crawl, rels)
	
	extension = filename.rsplit(".",1)[1]
	f = None
	if extension=="bz2":
		f = bz2.BZ2File(filename)
	elif extension=="gz":
		f = gzip.open(filename)
	
	this_name = None
	pkg = {}

	joins = []
	for line in f:
		line = line.strip("\n")
		if line == "":
			epoch, version, revision = parse_version(pkg["Version"])
			
			for join in joins:
				pkg[join] = "".join(pkg[join])
			joins = []
			# name, version, revision, time, additional
			rel = DownstreamRelease()
			rel.repo_id = repo.id
			rel.version = version
			rel.package = pkg["Package"]
			rel.revision = revision
			rel.released = last_modified
			rels.append(rel)
			pkg = {}
		elif line.startswith((" ","\t")):
			try:
				pkg[this_name].append(line)
			except:
				pkg[this_name] = [pkg[this_name],line]
				joins.append(this_name)
		else:
			try:
				name, value = line.split(":",1)
				pkg[name] = value.strip()
				this_name = name
			except:
				print
				print "ERROR: bad package line:",line
				return None
	
	return (last_modified, rels)
