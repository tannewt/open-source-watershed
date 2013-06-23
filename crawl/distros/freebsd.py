# -*- coding: utf-8 -*-
import time
import sys
import ftplib
sys.path.append(".")

from utils import helper
from utils.db import downstream
from utils.types import Repo, DownstreamRelease

CRAWL_DIR = "http://ftp.freebsd.org/pub/FreeBSD/ports/"

ARCHES = ["amd64", "arm", "i386", "ia64", "powerpc", "sparc64", "sun4v"]

distro_id = downstream.distro("freebsd", "", "A fixed release binary BSD distribution.", "http://www.freebsd.org")

def get_repos(test):
	repos = []
	current_version = None
	for arch in ARCHES[0:1]:
		directory = helper.open_dir(CRAWL_DIR + arch + "/")
		if directory == None:
		  print arch, "skipped"
		  continue
		for is_dir, filename, mod_time in directory:
			if filename.count("-")==2:
				pkg, version, branch = filename.split("-")
				repo = Repo()
				repo.distro_id = distro_id
				repo.component = pkg
				repo.architecture = arch
				print branch
				if branch == "stable" or branch == "current":
				  try:
				    repo.codename = int(version)
				  except:
				    continue
				elif branch == "release":
				  try:
				    repo.codename = float(version)
				  except:
				    continue
				repo.branch = branch
				repos.append(repo)
				downstream.repo(repo, test)
				if branch=="current" and (current_version == None or repo.codename > current_version):
					current_version = repo.codename
	
	for repo in repos:
		print repo.codename
		if repo.codename >= current_version:
			downstream.add_branch(repo, "current", test)
		elif repo.codename >= current_version-1 and repo.codename < current_version:
			downstream.add_branch(repo, "lts", test)
		else:
			downstream.add_branch(repo, "past", test)
	return repos

def crawl_repo(repo):
	rels = []
	fn = "".join(("files/freebsd/",str(repo.component),"-",str(time.time()),".txt"))
	url = "".join((CRAWL_DIR,repo.architecture,"/packages-",str(repo.codename),"-",repo.branch,"/INDEX"))
	t = helper.open_url(url,fn,repo.last_crawl)
	if t:
			f = open(fn)
			for line in f:
				pkg_ver = line.split("|",1)
				pkg, ver = pkg_ver[0].rsplit("-",1)
				if "," in ver:
					ver = ver.rsplit(",",1)[0]
				if "_" in ver:
					ver, rev = ver.rsplit("_",1)
				else:
					rev = "0"
				rel = DownstreamRelease()
				rel.repo_id = repo.id
				rel.package = pkg
				rel.version = ver
				rel.revision = rev
				rel.released = t
				rels.append(rel)
			f.close()
	if t == None:
		t = repo.last_crawl
	return (t, rels)

if __name__=="__main__":
	repos = get_repos(True)
	for repo in repos:
		print repo
	
		rels = crawl_repo(repo)
		print rels[0],len(rels[1]),"releases"
		print
	
