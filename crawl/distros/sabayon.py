# -*- coding: utf-8 -*-
import sqlite3
import datetime
import time
import subprocess
from utils import helper
from utils.db import downstream
from utils.types import Repo, DownstreamRelease

distro_id = downstream.distro("sabayon", "", "A binary distribution derived from Gentoo.", "http://www.sabayonlinux.org")

MIRROR = "http://mirror.umd.edu/sabayonlinux"
HTTP_START_DIR = "pub/SabayonLinux"
FTP_START_DIR = "pub/sabayonlinux"

VERSIONS = ["4", "5"]
CURRENT = "5"
FUTURE = ""

ARCHES = ["amd64", "x86", "armel", "armv7l"]

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos(test):
	repos = []
	for v in VERSIONS:
		for a in ARCHES:
			branch = "past"
			if v==CURRENT:
				branch = "current"
			elif v==FUTURE:
				branch = "future"
			repo = Repo()
			repo.distro_id = distro_id
			repo.codename = v
			repo.component = ""
			repo.architecture = a
			downstream.repo(repo, test)
			downstream.add_branch(repo, branch, test)
			repos.append(repo)
	return repos

# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
	fn = "".join(("files/sabayon/packages-",repo.codename,"-",repo.architecture,"-",str(time.time()),".db"))
	url = "".join((MIRROR,"/entropy/standard/sabayonlinux.org/database/", repo.architecture, "/", repo.codename, "/packages.db.bz2"))
	
	#print "open url"
	t = helper.open_url(url,fn+".bz2", repo.last_crawl)
	
	if t==None:
		return (repo.last_crawl, [])
	
	#print "extract"
	try:
		p = subprocess.Popen(("bunzip2",fn+".bz2"),stdout=None)
		x = p.wait()
	except OSError, e:
		print e
		x=-1
	
	#print "sql stuff"
	conn = sqlite3.connect(fn)
	c = conn.cursor()
	#print "go sql"
	c.execute("SELECT baseinfo.name, baseinfo.version, baseinfo.revision, baseinfo.branch, extrainfo.datecreation FROM baseinfo, extrainfo WHERE baseinfo.idpackage = extrainfo.idpackage;")
	#print "sql done"
	
	rels = []
	for name, version, revision, branch, date in c:
		dt = datetime.datetime.utcfromtimestamp(float(date))
		if repo.last_crawl==None or repo.last_crawl<dt:
			#print version
			if "-" in version and "-" == version[-3]:
				version, gentoo_revision = version.rsplit("-")
				revision = str(gentoo_revision[1:]) + "." + str(revision)
			rel = DownstreamRelease()
			rel.package = name
			rel.version = str(version)
			rel.revision = str(revision)
			rel.released = dt
			rels.append(rel)
	return t, rels
