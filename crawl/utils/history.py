# -*- coding: utf-8 -*-
import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper
from utils.version import VersionTree
from utils.timeline import *

HOST, USER, PASSWORD, DB = helper.mysql_settings()

VERBOSE = False
VERBOSE_RESULT = False

class PackageHistory:
	def __init__(self, name, threshold = 255, force_approx = False):
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
			sid = row[0]
		
		cur.execute("SELECT name, description FROM packages WHERE id = %s",(sid,))
		sname, self.description = cur.fetchone()
		
		if VERBOSE:
			print "found real name",sname
		self.name = sname
		
		explore = [sid]
		aliases = [self.name]
		while len(explore)>0:
			tmp = []
			for sid in explore:
				cur.execute("SELECT package_id2, packages.name FROM packages,links WHERE package_id1 = %s AND package_id2=packages.id AND strength >= %s",(sid,threshold))
				for row in cur:
					aliases.append(row[1])
					tmp.append(row[0])
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
		if VERBOSE:
			print self.aliases
		
		self.ish = False
		#print "query upstream"
		if not force_approx:
			q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND ("+ " OR ".join(("packages.name=%s",)*len(aliases)) + ") AND releases.version!='9999' AND releases.repo_id IS NULL GROUP BY releases.version ORDER BY MIN(releases.released), releases.version"
			cur.execute(q,aliases)
		if cur.rowcount == 0 or force_approx:
			if VERBOSE:
				print "falling back to approximate upstream"
			self.ish = True
			q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s AND releases.version!='9999' AND releases.repo_id IS NOT NULL GROUP BY releases.version ORDER BY MIN(releases.released), releases.version"
			cur.execute(q,(self.name,))
		
		data = []
		if VERBOSE:
			print "upstream"
		for version,date in cur:
			if VERBOSE:
				print version,date
			data.append((date, version))
		
		self.timeline = Timeline(data)
		self.count = DayTimeline(data,default=[])
		
		con.close()
	
	def __str__(self):
		if self.ish:
			pre = "approx history of "
		else:
			pre = "history of "
		return "\n".join((pre+self.name,str(self.timeline),"release count",str(self.count)))
		

class DistroHistory:
	def __init__(self, name, packages=[], branch=None, codename=None, arch=None, now=None):
		self._timeline = ConnectedTimeline(default=timedelta())
		self._obs_timeline = StepTimeline(default=0.0)
		self._bin_obs_timeline = StepTimeline(default=0.0)
		self.timeline = self._timeline
		self.obs_timeline = self._obs_timeline
		self.bin_obs_timeline = self._bin_obs_timeline
		self.notes = Timeline(default="")
		self.count = StepTimeline()
		self.fcount = StepTimeline()
		self.name = name
		self.branch = branch
		self.codename = codename
		
		con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
		cur = con.cursor()
		cur.execute("SELECT id, color FROM distros WHERE name = %s",(name))
		self.id, self.color = cur.fetchone()
		con.close()
		
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
	
	def get_pkg(self, name):
		return self._packages[name][1]
	
	def add_pkg(self, package):
		upstream = package.timeline
		downstream = self.get_downstream(package)
		if len(downstream)>0:
			age = self._compute_package_age(upstream, downstream)
			obs = self._compute_package_obsoletion(upstream, downstream)
			bin_obs = StepTimeline()
			for date in obs:
				if obs[date] > 0:
					bin_obs[date] = 1.0
				else:
					bin_obs[date] = 0.0
		else:
			age = ConnectedTimeline()
			obs = StepTimeline()
			bin_obs = StepTimeline()
		self._packages[package.name] = (package,downstream,age,obs)
		self._pkg_order.append(package.name)
		#print self.timeline
		#print age
		self._timeline = self._timeline + age
		self._obs_timeline = self._obs_timeline + obs
		self._bin_obs_timeline = self._bin_obs_timeline + bin_obs
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
			self.fcount = self.fcount + StepTimeline([(age.keys()[0],1.0)])
		
		self.timeline = self._timeline / self.count
		self.obs_timeline = self._obs_timeline / self.fcount
		self.bin_obs_timeline = self._bin_obs_timeline / self.fcount
	
	def get_downstream(self, package, revisions=False):
		con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
		cur = con.cursor()
		if self.name not in package.aliases:
			return Timeline()
		if revisions:
			q_start = "SELECT releases.version, releases.revision, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND ("+ " OR ".join(("packages.name=%s",)*len(package.aliases[self.name])) + ") AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s AND releases.version!='9999'"
			q_end = "GROUP BY releases.version, releases.revision ORDER BY MIN(releases.released), releases.version, releases.revision"
		else:
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
		if revisions:
			for version, revision, date in cur:
				if VERBOSE:
					print version, revision, date
				downstream[date] = (version, revision)
		else:
			for version, date in cur:
				if VERBOSE:
					print version, date
				downstream[date] = version

		if VERBOSE:
			print
		return downstream
	
	def _compute_package_age(self, upstream, downstream):
		ms = timedelta(microseconds=1)
		versions = VersionTree()
		age = ConnectedTimeline(default=timedelta())
		greatest_downstream = "0"
		u = 0
		d = 0
		#print
		#print "interleave"
		#interleave the dates
		while u+d < len(upstream)+len(downstream):
			version = None
			date = None
			if u<len(upstream) and (len(downstream)==d or upstream.keys()[u]<=downstream.keys()[d]):
				if VERBOSE:
					print "upstream",upstream.keys()[u],upstream[u]
				date = upstream.keys()[u]
				version = upstream[u]
				versions.add_release(date,version)
				if greatest_downstream != "0":
					age[date] = versions.compute_lag(date, greatest_downstream)
				u+=1
			else:
				version = downstream[d]
				date = downstream.keys()[d]
				if VERBOSE:
					print "downstream", date, version
				
				if VERBOSE:
					print greatest_downstream, version
				if greatest_downstream != "0":
					age[date] = versions.compute_lag(date, greatest_downstream)
				greatest_downstream = versions.max(greatest_downstream,version)
				if VERBOSE:
					print greatest_downstream
				age[date+ms] = versions.compute_lag(date, greatest_downstream)
				d+=1
		#print
		#print "age"
		now = self._now
		if now==None:
			now = datetime.now()
		if greatest_downstream!=None:
			age[now] = versions.compute_lag(now, greatest_downstream)
		
		if VERBOSE or VERBOSE_RESULT:
			for a in age:
				print a,age[a]
			print
		return age
	
	def _compute_package_obsoletion(self, upstream, downstream):
		ms = timedelta(microseconds=1)
		versions = VersionTree()
		age = StepTimeline()
		greatest_downstream = "0"
		u = 0
		d = 0
		#print
		#print "interleave"
		#interleave the dates
		while u+d < len(upstream)+len(downstream):
			version = None
			date = None
			if u<len(upstream) and (len(downstream)==d or upstream.keys()[u]<=downstream.keys()[d]):
				if VERBOSE:
					print "upstream",upstream.keys()[u],upstream[u]
				date = upstream.keys()[u]
				version = upstream[u]
				versions.add_release(date,version)
				if greatest_downstream != "0":
					age[date] = versions.compute_obsoletions(date, greatest_downstream)
				u+=1
			else:
				if VERBOSE:
					print "downstream",downstream.keys()[d],downstream[d]
				version = downstream[d]
				date = downstream.keys()[d]
				if VERBOSE:
					print greatest_downstream, version
				greatest_downstream = versions.max(greatest_downstream,version)
				if VERBOSE:
					print greatest_downstream
				age[date+ms] = versions.compute_obsoletions(date, greatest_downstream)
				d+=1
		#print
		#print "age"
		now = self._now
		if now==None:
			now = datetime.now()
		if greatest_downstream!=None:
			age[now] = versions.compute_obsoletions(now, greatest_downstream)
		
		if VERBOSE or VERBOSE_RESULT:
			for a in age:
				print a,age[a]
			print
		return age

def get_upstream(history=True):
	con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
	cur = con.cursor()
	result = []
	q = cur.execute("SELECT DISTINCT name FROM packages, releases WHERE releases.package_id = packages.id AND releases.repo_id IS NULL")
	total = q
	i = 0
	for pkg in cur:
		#print pkg[0],i,"/",total
		if history:
			result.append(PackageHistory(pkg[0]))
		else:
			result.append(pkg[0])
		i += 1
	con.close()
	return result

def get_all(history=True):
	con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
	cur = con.cursor()
	result = []
	q = cur.execute("SELECT name FROM packages")
	total = q
	i = 0
	for pkg in cur:
		#print pkg[0],i,"/",total
		if history:
			result.append(PackageHistory(pkg[0]))
		else:
			result.append(pkg[0])
		i += 1
	con.close()
	return result

if __name__=="__main__":
	if len(sys.argv)<2:
		print sys.argv[0],"<package>","[threshold]","[distro]","[branch]"
		sys.exit(1)
	#VERBOSE = True
	p = sys.argv[1]
	t = 255
	d = None
	b = "current"
	if len(sys.argv)>2:
		t = sys.argv[2]
	
	if len(sys.argv)>3:
		d = sys.argv[3]
	
	if len(sys.argv)>4:
		b = sys.argv[4]

	p = PackageHistory(p,t)
	print p
	
	if d != None:
		d = DistroHistory(d,[p],b)
		print d.timeline
		print d.obs_timeline
