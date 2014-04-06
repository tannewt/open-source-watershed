# -*- coding: utf-8 -*-
import xml.etree.cElementTree as xml
import datetime
import gzip
import time
from utils import helper
from utils.db import downstream
from utils.types import Repo, DownstreamRelease

distro_id = downstream.distro("fedora", "", "A popular binary distribution by RedHat.", "http://www.fedoraproject.org")

MIRROR = "mirrors.kernel.org"
HTTP_START_DIR = "fedora"
FTP_START_DIR = HTTP_START_DIR

NAMESPACE = "{http://linux.duke.edu/metadata/common}"
REPO_NAMESPACE = "{http://linux.duke.edu/metadata/repo}"

ARCHES = ["i386", "x86_64"]

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos(test):
	#list dirs in /releases
	repos = []
	files = map(lambda s: s[1][:-1],helper.open_dir("http://"+MIRROR+"/"+HTTP_START_DIR+"/releases"))
	releases = []
	print releases
	#get the releases
	for f in files:
		if f!="test":
			releases.append(int(f))
	
	for rel in releases:
		if rel==max(releases):
			branch="current"
		else:
			branch="past"
		for arch in ARCHES:
			r = Repo()
			r.distro_id = distro_id
			r.codename = str(rel)
			r.component = "Everything"
			r.architecture = arch
			r.development = False
			downstream.repo(r, test)
			downstream.add_branch(r, branch, test)
			repos.append(r)
			
			r = Repo()
			r.distro_id = distro_id
			r.codename = str(rel)
			r.component = "Testing"
			r.architecture = arch
			r.development = False
			downstream.repo(r, test)
			downstream.add_branch(r, branch, test)
			repos.append(r)
	
	for arch in ARCHES:
		r = Repo()
		r.distro_id = distro_id
		r.codename = str(max(releases)+1)
		r.component = "Everything"
		r.architecture = arch
		r.development = True
		downstream.repo(r, test)
		downstream.add_branch(r, "future", test)
		repos.append(r)

	return repos

# return a list of [name, version, revision, time, extra]
def crawl_repo(repo):
	primaries = []
	url_tail = "repodata/primary.xml.gz"
	url_start = "/".join(["http:/",MIRROR,HTTP_START_DIR])
	this_time =	str(time.mktime(datetime.datetime.now().timetuple()))
	file_end = "primary.xml.gz"
	file_start = "files/fedora/"
	if repo.development:
		site_branches = ["development/%s/os"%(repo.architecture)]
	elif repo.component == "Everything":
		site_branches = ["releases/%s/Everything/%s/os"%(repo.codename, repo.architecture), "updates/%s/%s"%(repo.codename, repo.architecture)]
	elif repo.component == "Testing":
		site_branches = ["updates/testing/%s/%s"%(repo.codename, repo.architecture)]
	else:
		site_branches = []
	
	last_crawl = None
	for site_branch in site_branches:
		filename = file_start+"-".join([this_time,site_branch.replace("/","_"),"repomd.xml"])
		url = "/".join([url_start,site_branch,"repodata/repomd.xml",])
		repomd = helper.open_url(url,filename,repo.last_crawl)
		
		if last_crawl == None or (repomd != None and last_crawl < repomd):
			last_crawl = repomd
		if repomd:
			print filename
			f = open(filename)
			repomd_tree = xml.parse(f)
			f.close()
			datas = repomd_tree.findall(REPO_NAMESPACE+"data")
			fn = None
			for data in datas:
				if data.attrib["type"]=="primary":
					loc = data.find(REPO_NAMESPACE+"location")
					if loc!=None:
						fn = loc.attrib["href"]
					break
			del datas
			del repomd_tree
			if fn:
				primaries.append(("/".join([url_start,site_branch,fn]),file_start+"-".join([this_time,site_branch.replace("/","_"),file_end])))
	
	rels = []
	for p,filename in primaries:
		print filename
		t = helper.open_url(p,filename,repo.last_crawl)
		if t==None:
			continue
		gzp = gzip.open(filename)
		print "opened"
		primary_tree = xml.parse(gzp)
		print "parsed"
		gzp.close()
		print "closed"
		
		i = primary_tree.getiterator(NAMESPACE + "package")

		for e in i:
			name = e.find(NAMESPACE + "name").text
			v = e.find(NAMESPACE + "version").attrib
			rel_time = e.find(NAMESPACE + "time").attrib["file"]
			version = v["ver"]
			revision = v["rel"]
			rel_time = datetime.datetime.utcfromtimestamp(float(rel_time))
			rel = DownstreamRelease()
			rel.repo_id = repo.id
			rel.version = version
			rel.package = name
			rel.revision = revision
			rel.released = rel_time
			rels.append(rel)
		del i
		del primary_tree
	
	if last_crawl==None:
		last_crawl = repo.last_crawl
	print "return",last_crawl,len(rels)
	return (last_crawl, rels)
