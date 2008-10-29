import xml.etree.ElementTree as xml
import datetime
import ftplib
import gzip
import time
from .utils import helper

MIRROR = "mirrors.kernel.org"
HTTP_START_DIR = "fedora"
FTP_START_DIR = HTTP_START_DIR

NAMESPACE = "{http://linux.duke.edu/metadata/common}"
REPO_NAMESPACE = "{http://linux.duke.edu/metadata/repo}"

ARCHES = ["i386", "ppc", "ppc64", "x86_64"]

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos():
  #list dirs in /releases
  repos = []
  ftp = ftplib.FTP(MIRROR)
  ftp.login()
  
  ftp.cwd(FTP_START_DIR+"/releases")
  files = ftp.nlst()
  releases = []
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
      repos.append(["fedora", branch, str(rel), "Everything", arch, None, None])
      repos.append(["fedora", branch, str(rel), "Testing", arch, None, None])
  
  for arch in ARCHES:
    repos.append(["fedora", "future", str(max(releases)+1), "Everything", arch, None, None])
  
  ftp.quit()
  return repos

# return a list of [name, version, revision, time, extra]
def crawl_repo(repo):
  name, branch, codename, comp, arch, last_crawl, new = repo
  
  primaries = []
  url_tail = "repodata/primary.xml.gz"
  url_start = "/".join(["http:/",MIRROR,HTTP_START_DIR])
  this_time =  str(time.mktime(datetime.datetime.now().timetuple()))
  file_end = "primary.xml.gz"
  file_start = "files/fedora/"
  if branch=="future":
    filename = file_start+"-".join([this_time,"devel","repomd.xml"])
    repomd = helper.open_url("/".join([url_start,"development",arch,"os/repodata/repomd.xml",]),filename,last_crawl)
    if repomd:
      f = open(filename)
      repomd_tree = xml.parse(f)
      datas = repomd_tree.findall(REPO_NAMESPACE+"data")
      fn = None
      for data in datas:
        if data.attrib["type"]=="primary":
          loc = data.find(REPO_NAMESPACE+"location")
          if loc!=None:
            fn = loc.attrib["href"]
          break
      if fn:
        primaries.append(("/".join([url_start,"development",arch,"os",fn]),file_start+"-".join([this_time,"devel",file_end])))
  else:
    if comp == "Everything":
      primaries.append(("/".join([url_start,"releases",codename,"Everything",arch,"os",url_tail]),file_start+"-".join([this_time,"devel",file_end])))
      primaries.append(("/".join([url_start,"updates",codename,arch,url_tail]),file_start+"-".join([this_time,"devel",file_end])))
    elif comp == "Testing":
      primaries.append(("/".join([url_start,"updates/testing",codename,arch,url_tail]),file_start+"-".join([this_time,"devel",file_end])))
  
  pkgs = []
  for p,filename in primaries:
    t = helper.open_url(p,filename,last_crawl)
    if t==None:
      continue
    gzp = gzip.open(filename)
    primary_tree = xml.parse(gzp)
    
    i = primary_tree.getiterator(NAMESPACE + "package")

    for e in i:
      name = e.find(NAMESPACE + "name").text
      v = e.find(NAMESPACE + "version").attrib
      rel_time = e.find(NAMESPACE + "time").attrib["file"]
      version = v["ver"]
      revision = v["rel"]
      epoch = v["epoch"]
      rel_time = datetime.datetime.fromtimestamp(float(rel_time))
      
      pkgs.append([name, version, revision, epoch, rel_time, xml.tostring(e)])
  return pkgs
  
