import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper
from utils.timeline import *

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = False
VERBOSE_RESULT = False

class PackageHistory:
  def __init__(self, name, threshold = 255):
    self.name = name
    # find the package name aliases
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    cur.execute("SELECT id FROM packages WHERE name = %s",(name,))
    result = cur.fetchone()
    if result == None:
      raise Exception("unknown package")
    else:
      sid = result[0]
    
    while True:
      cur.execute("SELECT package_id1 FROM links WHERE package_id2 = %s AND strength >= %s",(sid,threshold))
      row = cur.fetchone()
      if row==None:
        break
      print row[0],sid
      sid = row[0]
    
    cur.execute("SELECT name FROM packages WHERE id = %s",(sid,))
    sname = cur.fetchone()[0]
    
    print "found real name",sname
    self.name = sname
    
    explore = [sid]
    aliases = [self.name]
    while len(explore)>0:
      tmp = []
      for sid in explore:
        cur.execute("SELECT package_id2,packages.name FROM packages,links WHERE package_id1 = %s AND package_id2=packages.id AND strength >= %s",(sid,threshold))
        for row in cur:
          aliases.append(row[1])
          tmp.append(row[0])
          print row[0],sid
      explore = tmp
    
    #print "aliases",aliases
    
    distro_aliases = {}
    for alias in aliases:
      cur.execute("SELECT DISTINCT distros.name FROM releases,packages,repos,distros WHERE packages.id = releases.package_id AND releases.repo_id = repos.id AND distros.id = repos.distro_id AND packages.name = %s",(alias,))
      for row in cur:
        if row[0] not in distro_aliases:
          distro_aliases[row[0]] = [alias]
        else:
          distro_aliases[row[0]].append(alias)
    self.aliases = distro_aliases
    
    self.ish = False
    #print "query upstream"
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND ("+ " OR ".join(("packages.name=%s",)*len(aliases)) + ") AND releases.version!='9999' AND releases.repo_id IS NULL GROUP BY releases.version ORDER BY MIN(releases.released), releases.version"
    cur.execute(q,aliases)
    if cur.rowcount == 0:
      print "falling back to approximate upstream"
      self.ish = True
      q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released), releases.version"
      cur.execute(q,(self.name,))
    
    self.timeline = Timeline()
    if VERBOSE:
      print "upstream"
    for version,date in cur:
      if VERBOSE:
        print version,date
      self.timeline[date] = version
    
    con.close()
  
  def __str__(self):
    if self.ish:
      pre = "approx history of "
    else:
      pre = "history of "
    return "\n".join((pre+self.name,str(self.timeline)))
    

class DistroHistory:
  def __init__(self, name, packages=[], branch=None, codename=None, arch=None, now=None):
    self._timeline = ConnectedTimeline()
    self.notes = Timeline()
    self.count = StepTimeline()
    self.name = name
    self.branch = branch
    self.codename = codename
    self.arch = arch
    self._now = now
    
    # map a package name to a PackageHistory and ConnectedTimeline
    self._packages = {}
    # packages not used to compute distro history
    self._hidden = []
    self._pkg_order = []
    
    for p in packages:
      self.add_pkg(p)
  
  def snapshot(self, date):
    result = []
    for p in self._pkg_order:
      result.append((self._packages[p][1].last(date),self._packages[p][2][date]))
    return result
  
  def add_pkg(self, package):
    upstream = package.timeline
    downstream = self._get_downstream(package)
    age = self._compute_package_age(upstream, downstream)
    self._packages[package.name] = (package,downstream,age)
    self._pkg_order.append(package.name)
    #print self.timeline
    #print age
    self._timeline = self._timeline + age
    #print "result",self.timeline
    #print
    ms = timedelta(microseconds=1)
    for date in downstream:
      d = date + ms
      note = package.name+": "+downstream[date]
      if self.notes[d]!=None:
        self.notes[d] += "\n" + note
      else:
        self.notes[date+ms] = note
    if len(age.keys())>0:
      self.count = self.count + StepTimeline([(age.keys()[0],1)])
    
    self.timeline = self._timeline / self.count
  
  def _get_downstream(self, package):
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    if self.name not in package.aliases:
      return Timeline()
    q_start = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND ("+ " OR ".join(("packages.name=%s",)*len(package.aliases[self.name])) + ") AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999'"
    q_end = "GROUP BY releases.version ORDER BY MIN(releases.released), releases.version"
    if self.branch==None and self.arch==None:
      cur.execute(" ".join((q_start,q_end)),package.aliases[self.name]+[self.name])
    elif self.branch==None:
      q = " ".join((q_start,"AND repos.architecture=%s",q_end))
      cur.execute(q,package.aliases[self.name]+[self.name,self.arch])
    elif self.arch==None:
      q = " ".join((q_start,"AND repos.branch=%s",q_end))
      cur.execute(q,package.aliases[self.name]+[self.name,self.branch])
    else:
      q = " ".join((q_start,"AND repos.architecture=%s","AND repos.branch=%s",q_end))
      cur.execute(q,package.aliases[self.name]+[self.name,self.arch,self.branch])

    downstream = Timeline()
    if VERBOSE:
      print "downstream"
    for version, date in cur:
      if VERBOSE:
        print version, date
      downstream[date] = version

    if VERBOSE:
      print
    return downstream
  
  def _compute_package_age(self, upstream, downstream):
    ms = timedelta(microseconds=1)
    upstreams = {}
    latest = []
    age = ConnectedTimeline()
    last_downstream = None
    ds = False
    u = 0
    d = 0
    #print
    #print "interleave"
    #interleave the dates
    while u+d < len(upstream)+len(downstream):
      is_u = False
      version = None
      date = None
      append = False
      if u<len(upstream) and (len(downstream)==d or upstream[u][0]<=downstream[d][0]):
        if VERBOSE:
          print "upstream",upstream[u]
        date, version = upstream[u]
        upstreams[version] = date
        is_u = True
        append = len(downstream)==d or upstream[u][0]!=downstream[d][0]
        u+=1
      else:
        if VERBOSE:
          print "downstream",downstream[d]
        date, version = downstream[d]
        last_downstream = version
        append = True
        d+=1
      if ds and append:
        if len(latest)==0:
          age[date] = date-date
        else:
          age[date] = date-upstreams[latest[0]]
      if is_u:
        latest.append(version)
        #print latest
      else:
        while len(latest)>0  and latest.pop(0)!=version:
          pass
        #print latest
      if last_downstream!=None and append:
        ds=True
          
        if len(latest)==0:
          age[date+ms] = date-date
        else:
          age[date+ms] = date-upstreams[latest[0]]
    #print
    #print "age"
    now = self._now
    if now==None:
      now = datetime.now()
    if last_downstream!=None:
      if len(latest)==0:
        age[now] = now-now
      else:
        age[now] = now-upstreams[latest[0]]
    
    if VERBOSE or VERBOSE_RESULT:
      for a in age:
        print a,age[a]
      print
    return age

if __name__=="__main__":
  if len(sys.argv)<4:
    print sys.argv[0],"<package>","<threshold>","<distro>"
    sys.exit(1)
  p = PackageHistory(sys.argv[1],int(sys.argv[2]))
  print p
  d = DistroHistory(sys.argv[3],[p],"current")
  print d.timeline
