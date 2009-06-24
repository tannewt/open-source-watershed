# -*- coding: utf-8 -*-
import urllib
import ftplib
import time
import datetime
from .utils import helper
from .utils.db import downstream
from .utils.types import Repo, DownstreamRelease

MIRROR="slackware.osuosl.org"
FTP_START_DIR="pub/slackware/"
HTTP_START_DIR="/"

distro_id = downstream.distro("slackware", "", "A binary distribution by Patrick Volkerding.", "http://www.slackware.com")

def get_repos():
	files = helper.open_dir("ftp://"+MIRROR+"/"+FTP_START_DIR)
	releases = []
	for d,fn,date in files:
		if fn.count("-")==1:
			releases.append(fn)
	
	repos = []
	releases.remove("slackware-3.3")
	rs = []
	for r in releases:
		#print r
		r = r.split("-")[1]
		if r!="current":
			rs.append(float(r))
	
	for r in releases:
		arch, r = r.split("-")
		if r=="current":
			branch = "future"
		elif float(r)==max(rs):
			branch = "current"
		else:
			branch = "past"
		
		for comp in ["extra","pasture","patches",arch]:
			repo = Repo()
			repo.distro_id = distro_id
			repo.codename = r
			repo.component = comp
			if arch=="slackware":
				repo.architecture = "i486"
			elif arch=="slackware64":
				repo.architecture = "x86_64"
			repos.append(repo)
			
			downstream.repo(repo)
			
			if branch == "future":
				downstream.add_branch(repo, "future")
			elif branch == "current":
				downstream.add_branch(repo, "current")
			else:
				downstream.add_branch(repo, "past")
	
	return repos
	
def crawl_repo(repo):
	this_time = time.time()
	filename = "files/slackware/PACKAGES-" + repo.codename + "-" + repo.component + "-" + str(this_time) + ".TXT"
	if repo.architecture == "x86_64":
		prefix = "slackware64"
	else:
		prefix = "slackware"
	this_time = helper.open_url("http://" + MIRROR + HTTP_START_DIR + prefix + "-" + repo.codename + "/" + repo.component + "/PACKAGES.TXT",filename, repo.last_crawl)
	
	rels = []
	
	if this_time==None:
		return rels
	
	this_crawl_time = this_time
	
	#check to see if things have changed
	if repo.last_crawl and this_time<repo.last_crawl:
		return rels
	
	if repo.component == "slackware":
		k_filename = "files/slackware/VERSIONS-" + repo.codename + "-" + str(time.mktime(this_time.timetuple())) + ".TXT"
		k_time = helper.open_url("http://" + MIRROR + HTTP_START_DIR + prefix + "-" + repo.codename + "/kernels/VERSIONS.TXT",k_filename)
	
		kernel = open(k_filename).readlines()[1]
		kernel = kernel.split()
		kernel = kernel[kernel.index('version')+1].strip(".").strip(",")
		# name, version, revision, time, additional
		rel = DownstreamRelease()
		rel.repo_id = repo.id
		rel.package = "linux"
		rel.version = kernel
		rel.released = this_time
		rels.append(rel)
	
	pkg_file = open(filename)
	header = True
	last_empty = None
	pkg = {}
	for line in pkg_file:
		line = line.strip()
		
		if last_empty==None:
			if "html" in line or "HTML" in line:
				print
				print "bad url:",filename
				break;
			last_empty=False
		
		if header:
			this_empty = line==""
			header = not (last_empty and this_empty)
			last_empty = this_empty
		else:
			if line=="":
				if len(pkg.keys())>0:
					rel = DownstreamRelease()
					rel.repo_id = repo.id
					rel.package = pkg["name"]
					rel.version = pkg["version"]
					rel.revision = pkg["revision"]
					rel.released = this_time
					rels.append(rel)
				continue
			else:
				name, value = line.split(":",1)
			
			if name=="PACKAGE NAME":
				pkg["name"],pkg["version"],pkg["arch"],pkg["revision"]=value.strip()[:-4].rsplit("-",3)
			elif name==pkg["name"] or name=="PACKAGE DESCRIPTION":
				if pkg.has_key("description"):
					pkg["description"].append(value.strip()+"\n")
				else:
					pkg["description"] = [value.strip()]
			else:
				pkg[name] = value.strip()
	
	downstream.set_last_crawl(repo, this_crawl_time)
	return rels

def crawl():
	repos = get_repos()
	for repo in repos:
		rels = crawl_repo(repo)
		downstream.add_releases(repo, rels)