import os
import datetime
import cPickle as pickle
import re
import subprocess

MIRROR = "rsync.namerica.gentoo.org::gentoo-portage"
STORAGE = "files/gentoo/"
CACHE_FN = "cache.pickle"

FUNCTION_PATTERN = re.compile("^[a-z_]+[ \t]*\(\)")
VARIABLE_PATTERN = re.compile("^[A-Z]+=")

# return a list of ["ubuntu", branch, codename, component, arch, None, None]
def get_repos():
  repos = []
  f = open(STORAGE+"profiles/arch.list")
  arches = map(lambda s: s.strip(),f.readlines())
  f.close()
  for c,b in [("stable","current"),("unstable","future")]:
    for a in arches:
      repos.append(["gentoo",b,"",c,a,None,None])
  repos.append(["gentoo","past","","unknown","unknown",None,None])
  return repos

def parse(f):
  pkg = {}
  this_key = "unknown"
  variable = False
  function = False
  
  for line in f:
    f_match = FUNCTION_PATTERN.match(line)
    v_match = VARIABLE_PATTERN.match(line)
    line = line.strip()
    if line.startswith("#"):              #comments
      if not pkg.has_key("comments"):
        pkg["comments"]=[]
      pkg["comments"].append(line)
    elif v_match:  #variable
      v_match = v_match.group()
      key = v_match.split("=")[0].strip()
      val = line.strip(v_match).split("\"")
      try:
        if line.count("\"")==1:
          this_key = key
          pkg[key] = [val[1]]
        elif line.count("\"")==2:
          pkg[key] = val[1]
        else:
          pkg[key] = val[0]
      except:
        print v_match,val
    elif variable and "\"" in line:
      variable = False
      pkg[this_key].append(line.strip("\""))
      this_key = "unknown"
    elif f_match:  #function
      f_match = f_match.group()
      key = f_match.split("(")[0]
      if "{" in line:
        val = line.split("{")[1].split("}")[0]
      else:
        val = ""
      if "}" not in line:
        this_key = key
        pkg[key] = [val]
      else:
        pkg[key] = val
    elif function and line.strip()=="}":
      function = False
      this_key = "unknown"
    elif line.strip()=="":
      pass
    else:
      if not pkg.has_key(this_key):
        pkg[this_key] = []
      pkg[this_key].append(line.strip())
  return pkg

def crawl_changelog(category,package,last_crawl=None):
  fn = STORAGE+category+"/"+package+"/ChangeLog"
  last = os.stat(fn).st_mtime
  last = datetime.datetime.fromtimestamp(last)
  pkgs = []
  # check last crawl
  if last_crawl==None or last > last_crawl:
    try:
      f = open(fn)
    except:
      print "ERROR: opening %s"%fn
      return []
    
    for line in f:
      if line.startswith("*"+package) and " " in line:
        try :
          version,d,m,y  = line.strip().split()
          version = version.strip("*"+package+"-")
          d = d[1:]
          y = y[:-1]
          revision = 0
          if "-" in version:
            version, revision = version.rsplit("-",1)
            revision = int(revision[1:])
          released = datetime.datetime.strptime(" ".join((d,m,y)),"%d %b %Y")
          if last_crawl==None or released > last_crawl:
            pkgs.append([package, version, revision, 0, released, ""])
        except:
          print "ERROR: parsing '%s' in %s"%(line,fn)
    f.close()
  return pkgs
      
# return a list of [name, version, revision, epoch, time, extra]
def crawl_repo(repo):
  distro,branch,codename,component,arch,last_crawl,new = repo
  # check the cache
  try:
    last = os.stat(STORAGE+CACHE_FN)
  except OSError:
    print "no cache"
    last = None
  
  if last:
    last = last.st_mtime
    last = datetime.datetime.fromtimestamp(last)
    # check to make sure the cache is reasonably new
    if datetime.datetime.now()-last<datetime.timedelta(hours=1):
      # only load the cache if we have not crawled it already
      if last_crawl and last_crawl<last:
        #load the cache and return the desired subset
        f = open(STORAGE+CACHE_FN)
        cache = pickle.load(f)
        f.close()
        if cache.has_key(arch) and cache[arch].has_key(component):
          return cache[arch][component]
      return []
  
  # only do this if the cache is old
  
  # rsync up
  print "rsync",
  try:
    p = subprocess.Popen(("/usr/bin/rsync","-rt",MIRROR,STORAGE),stdout=None)
    x = p.wait()
  except OSError, e:
    print e
    x=-1
  
  if x != 0:
    print "ERROR: rsync failed: %s"%x
    return []
  
  pkgs = {"unknown":{"unknown":[]}}
  dirs = os.listdir(STORAGE)
  f = open(STORAGE+"profiles/categories")
  dirs = map(lambda s: s.strip(),f.readlines())
  f.close()
  for d in dirs:
    packages = os.listdir(STORAGE+d+"/")
    for p in filter(lambda x: x!="metadata.xml",packages):
      # crawl change log
      pkgs["unknown"]["unknown"] += crawl_changelog(d,p,last_crawl)
      for v in filter(lambda x: x.startswith(p+"-"), os.listdir(STORAGE+d+"/"+p+"/")):
        fn = STORAGE+d+"/"+p+"/"+v
        last = os.stat(fn).st_mtime
        last = datetime.datetime.fromtimestamp(last)
        
        # check last crawl
        if last_crawl==None or last > last_crawl:
          try:
            f = open(fn)
            pkg = parse(f)
          except:
            print "ERROR: parsing %s"%fn
            continue
          f.close()
          
          # parse v for version and revision
          v_split = v.strip(p+"-").strip(".ebuild").rsplit("-r",1)
          if len(v_split)==1:
            version = v_split[0]
            revision = 0
          else:
            version,revision = v_split
          
          pkg["filename"] = v
          
          first = True
          if not pkg.has_key("KEYWORDS"):
            print "WARNING: %s has no keywords."%(d+"/"+v)
            continue
          
          for kw in "".join(pkg["KEYWORDS"]).split(" "):
            if kw=="because" or kw=="all" or kw=="dont":
              print "WARNING: " + fn + " parsed keywords wrong"
            if not kw.startswith("-") and "*" not in kw:
              if "~" in kw:
                branch = "unstable"
                arch = kw.strip("~")
              else:
                branch = "stable"
                arch = kw
              
              if not pkgs.has_key(arch):
                pkgs[arch]={}
              
              if not pkgs[arch].has_key(branch):
                pkgs[arch][branch]=[]
              
              if first:
                extra = str(pkg)
                first = False
              else:
                extra = None
              pkgs[arch][branch].append([p, version, revision, 0, last, extra])
  
  # cache it
  f = open(STORAGE+CACHE_FN,"wb")
  pickle.dump(pkgs,f)
  f.close()
  if pkgs.has_key(arch) and pkgs[arch].has_key(component):
    return pkgs[arch][component]
  else:
    print "not found in cache"
    return []
