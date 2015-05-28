# -*- coding: utf-8 -*-
import json
import tarfile
import time
import sys
sys.path.append(".")

try:
    import lzma
except ImportError:
    from backports import lzma

from utils import helper
from utils.db import downstream
from utils.types import Repo, DownstreamRelease

RELEASE_DIR = "http://ftp.freebsd.org/pub/FreeBSD/releases/"
CRAWL_DIR = "http://pkg.freebsd.org/"

ARCHES = ["amd64", "i386"]

FIRST_PKG_RELEASE = 9

distro_id = downstream.distro("freebsd", "", "A fixed release binary BSD distribution.", "http://www.freebsd.org")

def get_repos(test):
	repos = []
	current_version = None
	for arch in ARCHES:
		directory = helper.open_dir(RELEASE_DIR + arch + "/")
		if directory == None:
		  print arch, "skipped"
		  continue
		for is_dir, filename, mod_time in directory:
                        print filename
			if filename.count("-")==1:
				version, branch = filename.split("-")
				repo = Repo()
				repo.distro_id = distro_id
				repo.architecture = arch
				try:
				  repo.codename = float(version)
				except:
				  continue
                                if repo.codename <= FIRST_PKG_RELEASE:
                                  continue
                                if repo.codename == None:
                                  continue
				repo.branch = branch
				repos.append(repo)
				downstream.repo(repo, test)
				if branch=="RELEASE/" and (current_version == None or repo.codename > current_version):
					current_version = repo.codename
	
        repos = sorted(repos, key=lambda x: x.codename, reverse=True)
        last_codename = None
	for repo in repos:
                if repo.codename > current_version:
                    downstream.add_branch(repo, "future", test)
		elif repo.codename == current_version:
		    downstream.add_branch(repo, "current", test)
		elif repo.codename >= current_version-1 and repo.codename < current_version and (last_codename == None or repo.codename == last_codename):
		    downstream.add_branch(repo, "lts", test)
                    if float(repo.codename) * 10 % 10 == 0:
                        last_codename = None
                    else:
                        last_codename = repo.codename
		else:
			downstream.add_branch(repo, "past", test)
	return repos

def crawl_repo(repo):
	rels = []
        major = str(int(repo.codename))
        minor = str(int(repo.codename * 10 % 10))
        arch = {"i386": "32", "amd64": "64"}[repo.architecture]
        directory = "freebsd:%s:x86:%s/release_%s" % (major, arch, minor)
	fn = "".join(("files/freebsd/",str(repo.component),"-",repo.architecture,"-",str(time.time()),".txz"))
	url = "".join((CRAWL_DIR,directory,"/packagesite.txz"))
	t = helper.open_url(url,fn,repo.last_crawl)
	if t:
	    f = lzma.open(fn)
            tf = tarfile.open(fileobj=f)
            packagesite = tf.extractfile("packagesite.yaml")
	    for line in packagesite:
                pkg = json.loads(line)
                ver = pkg["version"]
		if "_" in ver:
		    ver, rev = ver.rsplit("_",1)
		else:
		    rev = "0"
		rel = DownstreamRelease()
		rel.repo_id = repo.id
		rel.package = pkg["name"]
		rel.version = ver
		rel.revision = rev
		rel.released = t
		rels.append(rel)
            tf.close()
	    f.close()
	if t == None:
	    t = repo.last_crawl
	return (t, rels)

if __name__=="__main__":
	repos = get_repos(True)
	for repo in repos[:1]:
		print repo
	
		rels = crawl_repo(repo)
		print rels[0],len(rels[1]),"releases"
                for rel in rels[1][:10]:
                    print rel
		print
	
