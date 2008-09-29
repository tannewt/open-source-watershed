import distros.debian
import distros.slackware
import distros.ubuntu
import upstream.subversion
import MySQLdb as mysql
import datetime
import time

TEST = False
EXTRA = True

def crawl_distro(target):
  print "running",target.__name__
  repos = target.get_repos()
  
  if TEST:
    repos = repos[:1]

  con = mysql.connect(host='localhost', user='root', passwd='hello', db='test')

  cur = con.cursor()

  dist = (repos[0][0],)
  #check distro existance
  try:
    cur.execute("insert into distros(name) values (%s);",dist)
    cur.execute("select last_insert_id();");
  except mysql.IntegrityError:
    #print "found"
    cur.execute("select id from distros where name=%s", dist)
    
  distro_id = cur.fetchone()[0]
  #print "created:",distro_id

  #print "committing distro stuff"
  con.commit()
  
  # find unknown repos and mark them as new
  #print "gathering repo data"
  for repo in repos:
    cur.execute("select last_crawl from repos where distro_id=%s and branch=%s and codename=%s and component=%s and architecture=%s", [distro_id] + repo[1:-2])
    row = cur.fetchone()
    repo[-1] = row==None
    if row:
      repo[-2] = row[0]
  
  # build package cache
  cur.execute("select id, name from packages")
  cache_pkgs = {}
  for id, name in cur:
    cache_pkgs[name] = id

  #print "processing releases"
  for repo in repos:
    # pass in name, branch, codename, component, architecture, last_crawl and new
    print "crawling repo:"," ".join(repo[1:5]),
    try:
      rels = target.crawl_repo(repo)
    except IOError, e:
      print "ERROR: IOError: %s" % (e)
      rels = None
    
    if rels==None:
      print "ERROR: failed to crawl",repo
      continue
    #check to see if we have this repo
    #print "updating repo data"
    if repo[-1]:
      cur.execute("insert into repos (distro_id, branch, codename, component, architecture, discovered, last_crawl) values (%s,%s,%s,%s,%s,NOW(),NOW())", [distro_id] + repo[1:-2])
      cur.execute("select last_insert_id();")
      repo_id = cur.fetchone()[0]
    else:
      cur.execute("select id from repos where distro_id=%s and branch=%s and codename=%s and component=%s and architecture=%s", [distro_id] + repo[1:-2])
      repo_id = cur.fetchone()[0]
      cur.execute("update repos set last_crawl=NOW() where id=%s",(repo_id,))
    
    #print "processing repo releases"
    start_time = time.time()
    for rel in rels:
      #check to see if we have this package
      #pkg_id = cur.execute("select id from packages where name=%s",rel[0:1]).fetchone()
      if not cache_pkgs.has_key(rel[0]):
        #print "new package:",rel[0]
        try:
          cur.execute("insert into packages (name) values (%s);",rel[0:1])
          cur.execute("select last_insert_id();")
        except mysql.IntegrityError:
          cur.execute("select id from packages where name=%s",rel[0:1])
        
        pkg_id = cur.fetchone()[0]
        cache_pkgs[rel[0]]=pkg_id
      else:
        pkg_id = cache_pkgs[rel[0]]
      
      #check to see if we have this release
      if not repo[-1] or cur.fetchone()==None:
        try:
          cur.execute("insert into releases (package_id, version, revision, repo_id, released) values (%s,%s,%s,%s,%s)",(pkg_id,rel[1],rel[2],repo_id,rel[-2]))
          if EXTRA:
            cur.execute("select last_insert_id();")
            rel_id = cur.fetchone()[0]
            cur.execute("insert into extra (release_id, content) values (%s, %s)", (rel_id,rel[-1]))
        except mysql.IntegrityError:
          pass
    
    duration = time.time()-start_time
    if duration < 0.001:
      print "skipped"
    else:
      print duration,"secs"
    #print "committing"
    con.commit()
  con.close()
  print "done"
  print

def crawl_upstream(target):
  print "running",target.__name__,

  con = mysql.connect(host='localhost', user='root', passwd='hello', db='test')

  cur = con.cursor()
  
  cur.execute("select id,last_crawl from packages where name=%s",(target.NAME,))
  row = cur.fetchone()
  pkg_id = None
  last_crawl = None
  if row:
    pkg_id = row[0]
    last_crawl = row[1]
  else:
    cur.execute("insert into packages (name) values (%s)",(target.NAME,))
    cur.execute("select last_insert_id();");
    pkg_id = cur.fetchone()[0]
  
  for rel in target.get_releases(last_crawl):
    try:
      cur.execute("insert into releases (package_id, version, released) values (%s,%s,%s)",(pkg_id,rel[0],time.strftime("%Y-%m-%d %H:%M:%S",rel[1])))
      if EXTRA:
        cur.execute("select last_insert_id();")
        rel_id = cur.fetchone()[0]
        cur.execute("insert into extra (release_id, content) values (%s, %s)", (rel_id,rel[-1]))
    except mysql.IntegrityError:
      pass
  cur.execute("update packages set last_crawl=NOW() where id=%s",(pkg_id,))
  con.commit()
  con.close()
  print "done"

crawl_distro(distros.slackware)
crawl_distro(distros.debian)
crawl_distro(distros.ubuntu)

crawl_upstream(upstream.subversion)
