# -*- coding: utf-8 -*-
from .utils import helper
from .utils.db import downstream
from .utils.types import Repo, DownstreamRelease

distro_id = downstream.distro("opensuse", "", "Community version of Suse, a German binary distribution.", "http://www.opensuse.org")

MIRROR = "download.opensuse.org"
HTTP_START_DIR = ""
FTP_START_DIR = None
COMPONENTS = ["non-oss","oss"]
CURRENT = "11.1"
FUTURE = ""

def to_num(s):
	if "-" in s:
		return s.split("-")[0]
	return s

def get_repos(test):
	dists = helper.open_dir("http://"+MIRROR+"/distribution/")
	repos = []
	dists = filter(lambda x: x[0] and not x[1].startswith("openSUSE"), dists)
	for d,n,t in dists:
		codename = n.strip("/")
		for c in COMPONENTS:
			arches = helper.open_dir("http://"+MIRROR+"/distribution/"+n+"repo/"+c+"/suse/")
			if arches == None:
				continue
			for ad,an,at in filter(lambda x: x[0] and x[1]!="repodata/" and x[1]!="setup/",arches):
				arch = an.strip("/")
				repo = Repo()
				repo.distro_id = distro_id
				repo.codename = codename
				repo.component = c
				repo.architecture = arch
				downstream.repo(repo, test)
				repos.append(repo)
				if to_num(codename)==CURRENT:
					downstream.add_branch(repo, "current", test)
				elif to_num(codename)==FUTURE:
					downstream.add_branch(repo, "future", test)
				else:
					downstream.add_branch(repo, "past", test)
	for c in COMPONENTS:
		arches = helper.open_dir("http://"+MIRROR+"/factory/repo/"+c+"/suse/")
		for ad,an,at in filter(lambda x: x[0] and x[1]!="repodata/" and x[1]!="setup/",arches):
			arch = an.strip("/")
			repo = Repo()
			repo.distro_id = distro_id
			repo.codename = "factory"
			repo.component = c
			repo.architecture = arch
			downstream.repo(repo, test)
			repos.append(repo)
			downstream.add_branch(repo, "experimental", test)
	return repos
		
	

def crawl_repo(repo):
	rels = []
	if repo.codename=="factory":
		urls = []
		urls.append("http://" + MIRROR + "/factory/repo/"+repo.component + "/suse/" + repo.architecture + "/")
	else:
		urls = []
		urls.append("http://" + MIRROR + "/distribution/" + repo.codename + "/repo/" + repo.component + "/suse/" + repo.architecture + "/")
		if repo.component=="oss":
			urls.append("http://" + MIRROR + "/update/" + repo.codename + "/rpm/" + repo.architecture + "/")
			urls.append("http://" + MIRROR + "/update/" + repo.codename + "-test/rpm/" + repo.architecture + "/")
	
	pkg_lines = []
	for url in urls:
		lines = helper.open_dir(url)
		if lines==None:
			print "Nothing from:",url
			continue
		pkg_lines += lines
	
	last_crawl = repo.last_crawl
	for d,name,time in pkg_lines:
		if name=="MD5SUMS":
			continue
		if repo.last_crawl==None or repo.last_crawl<time:
			if last_crawl == None or time > last_crawl:
				last_crawl = time
			try:
				rest,arch,rpm = name.rsplit(".",2)
				name,version,revision = rest.rsplit("-",2)
			except:
				print "ERROR: cannot parse " + name
				continue
			rel = DownstreamRelease()
			rel.package = name
			rel.version = version
			rel.revision = revision
			rel.released = time
			rels.append(rel)
	return last_crawl, rels