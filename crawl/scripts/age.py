import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)

VERBOSE = False

def get_age(distro, package, branch=None, arch=None, now=None):
  cur = con.cursor()
  #print "query upstream"
  q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' AND releases.repo_id IS NULL GROUP BY releases.version ORDER BY MIN(releases.released)"
  cur.execute(q,(package,))
  if cur.rowcount == 0:
    print "falling back to approximate upstream"
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,))
  
  upstream = []
  if VERBOSE:
    print "upstream"
  for row in cur:
    if VERBOSE:
      print row
    upstream.append(row)
  
  if VERBOSE:
    print

  #print
  #print "query downstream"
  if branch==None and arch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro))
  elif branch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.architecture=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,arch))
  elif arch==None:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.branch=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,branch))
  else:
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999' AND repos.architecture=%s AND repos.branch=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro,arch,branch))

  downstream = []
  if VERBOSE:
    print "downstream"
  for row in cur:
    if VERBOSE:
      print row
    downstream.append(row)

  if VERBOSE:
    print
  upstreams = {}
  latest = []
  ages = []
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
    if u<len(upstream) and (len(downstream)==d or upstream[u][1]<=downstream[d][1]):
      if VERBOSE:
        print "upstream",upstream[u]
      version, date = upstream[u]
      upstreams[version] = date
      is_u = True
      append = len(downstream)==d or upstream[u][1]!=downstream[d][1]
      u+=1
    else:
      if VERBOSE:
        print "downstream",downstream[d]
      version, date = downstream[d]
      last_downstream = version
      append = True
      d+=1
    if ds and append:
      if len(latest)==0:
        ages.append((date, date-date, None))
      else:
        ages.append((date, date-upstreams[latest[0]], None))
      if VERBOSE:
        print ages[-1][1],latest
    if is_u:
      latest.append(version)
      #print latest
    else:
      while len(latest)>0  and latest.pop(0)!=version:
        pass
      #print latest
    if last_downstream!=None and append:
      ds=True
      note = None
      if is_u:
        note = "upstream: " + version
      else:
        note = "downstream: " + version
      if len(latest)==0:
        ages.append((date, date-date, note))
      else:
        ages.append((date, date-upstreams[latest[0]], note))
      if VERBOSE:
        print ages[-1][1],latest
  #print
  #print "age"
  if now==None:
    now = datetime.datetime.now()
  if last_downstream!=None:
    if len(latest)==0:
      ages.append((now, now-now))
    else:
      ages.append((now,now-upstreams[latest[0]]))
  
  if VERBOSE:
    print "age of",package
    for a in ages:
      print a
    print
  return ages

def sum_ages(aA, aB):
  a = 0
  b = 0
  last_aA = None
  last_aB = None
  result = []
  while a+b<len(aA)+len(aB)-2:
    # the next is in list A
    if a<len(aA)-1 and (len(aB)-1==b or aA[a][0]<aB[b][0]):
      # special case for start
      if a==0 and last_aB==None:
        a+=1
      elif a==0 and last_aB!=None:
        result.append((aA[0][0], aA[0][1]+last_aB[1]))
        a+=1
      elif last_aB!=None:
        result.append((aA[a][0], aA[a][1]+last_aB[1]))
        result.append((aA[a+1][0], aA[a+1][1]+last_aB[1]))
        a+=2
      else:
        a+=1
      last_aA = aA[a-1]
    #equal time start
    elif a==0 and b==0 and aA[a][0]==aB[b][0]:
      result.append((aA[a][0], aA[a][1]+aB[b][1]))
      last_aA = aA[a]
      last_aB = aB[b]
      a+=1
      b+=1
    # equal time non-start
    elif a>0 and b>0 and a<len(aA)-1 and b<len(aB)-1 and aA[a][0]==aB[b][0]:
      result.append((aA[a][0], aA[a][1]+aB[b][1]))
      result.append((aA[a][0], aA[a+1][1]+aB[b+1][1]))
      last_aA = aA[a+1]
      last_aB = aB[b+1]
      a+=2
      b+=2
    elif b<len(aB)-1 and (len(aA)-1==a or aA[a][0]>aB[b][0]):
      # special case for start
      if b==0 and last_aA==None:
        b+=1
      elif b==0 and last_aA!=None:
        result.append((aB[0][0], aB[0][1]+last_aA[1]))
        b+=1
      elif last_aA!=None:
        result.append((aB[b][0], aB[b][1]+last_aA[1]))
        result.append((aB[b+1][0], aB[b+1][1]+last_aA[1]))
        b+=2
      else:
        b+=1
      last_aB = aB[b-1]
    else:
      print "unseen case",a,b
      print aA[a]
      print aB[b]
      break
  result.append((aA[-1][0],aA[-1][1]+aB[-1][1]))
  if VERBOSE:
    print "combined"
    for a in result:
      print a
    print
  return result

def get_combined_age(distro, packages, branch=None, arch=None):
  combined = None
  now = datetime.datetime.now()
  for pkg in packages:
    points = get_age(distro, pkg, branch, arch, now)
    point = map(lambda x: (x[0], x[1]//len(packages)),points)
    if combined==None:
      combined = points
    else:
      combined = sum_ages(combined, points)
  return combined

if __name__ == "__main__":
  if "--verbose" in sys.argv:
    VERBOSE = True
    sys.argv.remove("--verbose")
    print "Being verbose."

  if len(sys.argv)<3:
    print sys.argv[0],"<distro> <package>*"

  get_combined_age(sys.argv[1],sys.argv[2:])
