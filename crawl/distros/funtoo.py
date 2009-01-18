import gentoo
import subprocess

STORAGE = "files/funtoo/portage/"
CACHE_FN = "cache.pickle"

def get_repos():
  repos = []
  print "funtoo repos"
  f = open(STORAGE+"profiles/arch.list")
  arches = map(lambda s: s.strip(),f.readlines())
  f.close()
  for c,b in [("stable","current"),("unstable","future")]:
    for a in arches:
      repos.append(["funtoo",b,"",c,a,None,None])
  return repos


def crawl_changelog(category,package,last_crawl=None):
  return []

def update_portage():
  # rsync up
  print "git-pull",
  try:
    p = subprocess.Popen(("/usr/bin/git-pull"),stdout=None,cwd=STORAGE)
    x = p.wait()
  except OSError, e:
    print e
    x=-1
  
  if x != 0:
    print "ERROR: git-pull failed: %s"%x
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
