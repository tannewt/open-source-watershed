# -*- coding: utf-8 -*-
import time
import datetime
import os
import urllib
import gzip
import sys
from utils import helper,deb
from utils.db import downstream
from utils.types import Repo, DownstreamRelease

distro_id = downstream.distro("debian", "", "An old binary distribution known for its stability.", "http://www.debian.org")

CN_ETCH="etch"
CN_LENNY="lenny"
CN_SARGE="sarge"
CN_SID="sid"
CN_SQUEEZE="squeeze"
CN_WHEEZY="wheezy"
CN_EXPERIMENTAL="experimental"

CODENAMES = [
	CN_LENNY,
	CN_SQUEEZE,
	CN_WHEEZY,
	CN_SID,
	CN_EXPERIMENTAL]

BRANCHES = {
	CN_ETCH : "past",
	CN_LENNY : "lts",
	CN_SARGE : "past",
	CN_SID : "experimental",
	CN_SQUEEZE : "current",
	CN_WHEEZY : "future",
	CN_EXPERIMENTAL : "experimental"}

MIRROR = "debian.osuosl.org"

START_DIR = "debian/dists/"

def get_repos(test):
	repos = []
	codename = None
	architectures = None
	components = None
	this_time = datetime.datetime.now()
	for codename in CODENAMES:
		for x in [None, "proposed-updates"]:
			if x!=None:
				crawl = codename + "-" + x
			else:
				crawl = codename
			#print "fetching", branch
			filename = "files/debian/Release-"+crawl+"-"+str(time.mktime(this_time.timetuple()))
			#print ["http://",MIRROR,"/",START_DIR,crawl,"/Release"]
			if None==helper.open_url("".join(["http://",MIRROR,"/",START_DIR,crawl,"/Release"]),filename):
				continue
			
			#print "parsing"
			
			for line in open(filename).readlines()[:9]:
				line = line.strip()
				#print line
				name, value = line.split(":")[:2]
				#print name
				if name == "Architectures":
					architectures=line.split(' ')[1:]
				elif name == "Components":
					components=line.split(' ')[1:]
			
			if not architectures:
				architectures = "alpha amd64 arm armel hppa i386 ia64 kfreebsd-i386 kfreebsd-amd64 mips mipsel powerpc s390 sparc".split(' ')
			
			#print components,architectures
			if not architectures or not components:
				print "Something is missing from debian %s"%crawl
			else:
				for arch in architectures:
					for comp in components:
						if x:
							comp += "|" + x
						repo = Repo()
						repo.distro_id = distro_id
						repo.codename = codename
						repo.component = comp
						repo.architecture = arch
						downstream.repo(repo, test)
						downstream.add_branch(repo, BRANCHES[codename], test)
						repos.append(repo)
	
	#print distros
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
	comp = repo.component
	codename = repo.codename
	arch = repo.architecture

	if "|" in comp:
		comp, test = comp.split("|")
		codename += "-" + test
	
	filename = "files/debian/Packages-" + codename + "-" + comp + "-" + arch + "-" + str(time.time()) + ".gz"
	url = "http://" + MIRROR + "/" + START_DIR + codename + "/" + comp + "/binary-" + arch + "/Packages.gz"
	
	lc_pkgs = deb.parse_packages(version_parser,filename,url,repo)
	return lc_pkgs
