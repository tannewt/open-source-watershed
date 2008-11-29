MIRROR = None
HTTP_START_DIR = None
FTP_START_DIR = None

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos():
  pass

# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
  distro,branch,codename,component,arch,last_crawl,new = repo
  pass
