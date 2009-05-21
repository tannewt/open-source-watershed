# -*- coding: utf-8 -*-
from .utils import helper

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

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
# past, lts, current, future, experimental
def get_repos():
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
				if to_num(codename)==CURRENT:
					repos.append(["opensuse", "current", codename, c, arch, None, None])
				elif to_num(codename)==FUTURE:
					repos.append(["opensuse", "future", codename, c, arch, None, None])
				else:
					repos.append(["opensuse", "past", codename, c, arch, None, None])
	for c in COMPONENTS:
		arches = helper.open_dir("http://"+MIRROR+"/factory/repo/"+c+"/suse/")
		for ad,an,at in filter(lambda x: x[0] and x[1]!="repodata/" and x[1]!="setup/",arches):
			arch = an.strip("/")
			repos.append(["opensuse", "experimental", "factory", c, arch, None, None])
	return repos
		
	

# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
	distro,branch,codename,component,arch,last_crawl,new = repo
	pkgs = []
	if branch=="experimental":
		urls = []
		urls.append("http://" + MIRROR + "/factory/repo/"+component+"/suse/"+arch+"/")
	else:
		urls = []
		urls.append("http://" + MIRROR + "/distribution/"+codename+"/repo/"+component+"/suse/"+arch+"/")
		if component=="oss":
			urls.append("http://" + MIRROR + "/update/"+codename+"/rpm/"+arch+"/")
			urls.append("http://" + MIRROR + "/update/"+codename+"-test/rpm/"+arch+"/")
	
	pkg_lines = []
	for url in urls:
		pkg_lines += helper.open_dir(url)
	
	for d,name,time in pkg_lines:
		if name=="MD5SUMS":
			continue
		if last_crawl==None or last_crawl<time:
			try:
				rest,arch,rpm = name.rsplit(".",2)
				name,version,revision = rest.rsplit("-",2)
			except:
				print "ERROR: cannot parse " + name
				continue
			pkgs.append([name,version,revision,0,time,""])
	return pkgs
	
