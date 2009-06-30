# -*- coding: utf-8 -*-
import time
import datetime
import os
import urllib
import bz2
import sys
from .utils import helper,deb
from .utils.db import downstream
from .utils.types import Repo, DownstreamRelease

distro_id = downstream.distro("ubuntu", "", "A popular debian based binary distribution.", "http://www.ubuntu.com")

CN_DAPPER="dapper"
CN_FEISTY="feisty"
CN_GUTSY="gutsy"
CN_HARDY="hardy"
CN_INTREPID="intrepid"
CN_JAUNTY="jaunty"
CN_KARMIC="karmic"

CODENAMES = [
	CN_DAPPER,
	CN_FEISTY,
	CN_GUTSY,
	CN_HARDY,
	CN_INTREPID,
	CN_JAUNTY,
	CN_KARMIC]

LTS = [CN_DAPPER, CN_HARDY]

ARCHES = {CN_DAPPER : ["amd64", "i386", "powerpc", "sparc"],
	CN_FEISTY : ["amd64", "i386", "powerpc", "sparc"],
	CN_GUTSY : ["amd64", "i386", "powerpc", "sparc"],
	CN_HARDY : ["amd64", "i386"],
	CN_INTREPID : ["amd64", "i386"],
	CN_JAUNTY : ["amd64", "i386"],
	CN_KARMIC : ["amd64", "i386"]}

MIRROR = "ubuntu.osuosl.org"

FTP_START_DIR = "pub/ubuntu/dists/"

HTTP_START_DIR = "ubuntu/dists/"

def get_repos():
	repos = []
	# find the codenames
	u = "".join(("http://",MIRROR,"/",HTTP_START_DIR))
	print u
	files = helper.open_dir(u)
	codenames = []
	for d,name,mod in files:
		if "-" not in name:
			codenames.append(name.strip("/"))
	
	for codename in CODENAMES:
		for repo in [None,"backports","proposed","security","updates"]:
			for arch in ARCHES[codename]:
				for component in ["main","multiverse","universe","restricted"]:
					if repo!=None:
						component += "|" + repo
					
					if codename == CODENAMES[-1]:
						branch = "future"
					elif codename == CODENAMES[-2]:
						branch = "current"
					elif codename == filter(lambda x: x!=CODENAMES[-1] and x!=CODENAMES[-2],LTS)[-1]:
						branch = "lts"
					else:
						branch = "past"
					
					r = Repo()
					r.distro_id = distro_id
					r.codename = codename
					r.component = component
					r.architecture = arch
					downstream.repo(r)
					downstream.add_branch(r, branch)
					repos.append(r)

	return repos

def version_parser(version):
	#[epoch:]upstream_version[-debian_revision] 
	if ":" in version:
		epoch, ver = version.split(":",1)
	else:
		ver = version
		epoch = 0

	if "-" in ver:
		ver, rev = ver.rsplit("-",1)
	else:
		rev = "0"
	
	# get rid of dfsg
	if "dfsg" in ver:
		ver, g_rev = ver.rsplit("dfsg",1)
		rev = g_rev + "." + rev
		if not (ver[-1].isdigit() or ver[-1].isalpha()):
			ver = ver[:-1]
		if not (rev[0].isdigit() or rev[0].isalpha()):
			rev = rev[1:]
	
	return epoch, ver, rev

def crawl_repo(repo):
	codename = repo.codename
	comp = repo.component
	arch = repo.architecture
	
	if "|" in comp:
		comp, test = comp.split("|")
		codename += "-" + test
	
	url = "http://" + MIRROR + "/" + HTTP_START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.bz2"
	filename = "files/ubuntu/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(time.time()) + ".bz2"
	
	#info = helper.open_url(url, filename, repo.last_crawl)
	lc_pkgs = deb.parse_packages(version_parser, filename, url, repo)
	
	return lc_pkgs