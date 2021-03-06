# -*- coding: utf-8 -*-
import gentoo
import os
import subprocess
from utils.db import downstream
from utils.types import Repo

distro_id = downstream.distro("funtoo", "", "A gentoo based source distribution.", "http://www.funtoo.org")
STORAGE = "files/funtoo/portage/"
CACHE_FN = "cache.pickle"

# git clone git://github.com/funtoo/portage.git

def get_repos(test):
        if not os.path.exists(STORAGE+"profiles/arch.list"):
		update_portage()
	repos = []
	print "funtoo repos"
	f = open(STORAGE+"profiles/arch.list")
	arches = map(lambda s: s.strip(),f.readlines())
	arches = arches[:arches.index("")]
	f.close()
	for c,b in [("stable","current"),("unstable","future")]:
		for a in arches:
			repo = Repo()
			repo.distro_id = distro_id
			repo.codename = ""
			repo.component = c
			repo.architecture = a
			downstream.repo(repo, test)
			downstream.add_branch(repo, b, test)
			repos.append(repo)
	return repos


def crawl_changelog(category,package,last_crawl=None):
	return []

def update_portage():
  # rsync up
  #print "git pull",
  try:
    p = subprocess.Popen(("/usr/bin/git","pull"),stdout=open("/dev/null","w"),cwd=STORAGE)
    x = p.wait()
  except OSError, e:
    print e
    x=-1
  
  if x != 0:
    print "ERROR: git pull failed: %s"%x
    return False
  return True

def crawl_repo(repo):
	gSTORAGE = gentoo.STORAGE
	gentoo.STORAGE = STORAGE
	gupdate_portage = gentoo.update_portage
	gentoo.update_portage = update_portage
	gcrawl_changelog = gentoo.crawl_changelog
	gentoo.crawl_changelog = crawl_changelog
	r = gentoo.crawl_repo(repo)
	gentoo.STORAGE = gSTORAGE
	gentoo.update_portage = gupdate_portage
	gentoo.crawl_changelog = gcrawl_changelog
	return r
