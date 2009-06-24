# -*- coding: utf-8 -*-
import distros.debian
import distros.slackware
import distros.ubuntu
import distros.fedora
import distros.gentoo
import distros.opensuse
import distros.arch
import distros.sabayon
import distros.funtoo

import gc
import traceback

import upstream.subversion
import upstream.postfix
import upstream.gnome
import upstream.gnu
import upstream.x
import upstream.gimp
import upstream.python
import upstream.apache
import upstream.db
import upstream.linux
import upstream.sf
import upstream.single_dir
import upstream.kde
import upstream.firefox
import upstream.php
import upstream.explore

from utils.cache import Cache

DISTROS = {"slackware": distros.slackware,
					 "debian"		: distros.debian,
					 "ubuntu"		: distros.ubuntu,
					 "fedora"		: distros.fedora,
					 "gentoo"		: distros.gentoo,
					 "opensuse"	: distros.opensuse,
					 "arch"			: distros.arch,
					 "sabayon"	: distros.sabayon,
					 "funtoo"		: distros.funtoo}

UPSTREAM = {"subversion": upstream.subversion,
						"postfix"		: upstream.postfix,
						"gnome"			: upstream.gnome,
						"gnu"				: upstream.gnu,
						"x"					: upstream.x,
						"gimp"			: upstream.gimp,
						"python"		: upstream.python,
						"db"				: upstream.db,
						"linux"			: upstream.linux,
						"sf"				: upstream.sf,
						"single_dir": upstream.single_dir,
						"kde"				: upstream.kde,
						"firefox"		: upstream.firefox,
						"php"				: upstream.php,
						"explore"		: upstream.explore}
						#"apache"		 : upstream.apache}

import utils.helper

import MySQLdb as mysql
import datetime
import time
import random
import sys
import cPickle as pickle

TEST = False
EXTRA = True

HOST, USER, PASSWORD, DATABASE = utils.helper.mysql_settings()

def crawl_distro(target, last=True):
	cache = Cache()
	repos = target.get_repos()
	format = "\n" + target.__name__ + " (%d/"+str(len(repos))+") +%d\n%s"
	release_count = 0
	if TEST:
		repos = [random.choice(repos)]

	con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)

	cur = con.cursor()

	dist = (repos[0][0],)
	#check distro existance

		
	distro_id = cur.fetchone()[0]
	#print "created:",distro_id

	#print "committing distro stuff"
	con.commit()
	
	# find unknown repos and mark them as new
	#print "gathering repo data"
	for repo in repos:
		cur.execute("SELECT crawls.time FROM crawls,repos WHERE repos.distro_id=%s AND repos.branch=%s AND repos.codename=%s AND repos.component=%s AND repos.architecture=%s AND crawls.repo_id=repos.id ORDER BY crawls.time DESC LIMIT 1", [distro_id] + repo[1:-2])
		row = cur.fetchone()
		repo[-1] = row==None
		if row and last:
			repo[-2] = row[0]
	
	# build package cache
	cur.execute("select id, name from packages")
	cache_pkgs = {}
	for id, name in cur:
		cache_pkgs[name] = id

	total_releases = 0
	i = 0
	#print "processing releases"
	for repo in repos:
		#pb.render(100*i/len(repos),format%(i,total_releases," ".join(repo[1:5])))
		# pass in name, branch, codename, component, architecture, last_crawl and new
		print "crawling:"," ".join(repo[1:5]),
		start_time = time.time()
		try:
			rels = target.crawl_repo(repo)
		except IOError, e:
			print "ERROR: IOError: %s" % (e)
			rels = None
		
		if rels==None:
			print "ERROR: failed to crawl",repo
			continue
		
		#check to see if we have this repo"
		if repo[-1]:
			cur.execute("insert into repos (distro_id, branch, codename, component, architecture, discovered) values (%s,%s,%s,%s,%s,NOW())", [distro_id] + repo[1:-2])
			cur.execute("select last_insert_id();")
			repo_id = cur.fetchone()[0]
		else:
			cur.execute("select id from repos where distro_id=%s and branch=%s and codename=%s and component=%s and architecture=%s", [distro_id] + repo[1:-2])
			repo_id = cur.fetchone()[0]
		
		release_count = 0
		
		#print "processing repo releases"
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
					cur.execute("insert into releases (package_id, version, revision, epoch, repo_id, released) values (%s,%s,%s,%s,%s,%s)",(pkg_id,rel[1],rel[2],rel[3],repo_id,rel[-2]))
					if EXTRA:
						cur.execute("select last_insert_id();")
						rel_id = cur.fetchone()[0]
						cur.execute("insert into extra (release_id, content) values (%s, %s)", (rel_id,rel[-1]))
					release_count += 1
					cache.evict([(pkg_id, distro_id)])
					
				except mysql.IntegrityError:
					pass
		
		duration = time.time()-start_time
		print "~"+str(int(duration)),"secs",
		#print "committing"
		con.commit()
		
		#add the crawl
		if release_count>0:
			cur.execute("insert into crawls (repo_id, release_count, time) values (%s,%s,NOW())", [repo_id,release_count])
			cache.evict([(None, distro_id)])
		else:
			cur.execute("insert into crawls (repo_id, time) values (%s,NOW())", [repo_id])
		con.commit()
		total_releases += release_count
		print release_count,"releases"
		i += 1
	con.close()
	del cache
	#print
	return total_releases

def crawl_upstream(target, last=True):
	print "running",target.__name__,
	cache = Cache()

	con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)

	# get this upstream id
	cur = con.cursor()
	cur.execute("SELECT id FROM packages WHERE name=%s",(target.NAME,))
	row = cur.fetchone()
	cpkg_id = None
	if row:
		cpkg_id = row[0]
	else:
		cur.execute("insert into packages (name) values (%s)",(target.NAME,))
		cur.execute("select last_insert_id();");
		cpkg_id = cur.fetchone()[0]
	
	# get the last crawl
	cur.execute("SELECT time FROM crawls WHERE package_id=%s ORDER BY time DESC LIMIT 1",(cpkg_id,))
	row = cur.fetchone()
	last_crawl = None
	if row and last:
		last_crawl = row[0]
		
	#print last_crawl,cpkg_id
	#last_crawl = None
	# crawl
	rels = target.get_releases(last_crawl)
	count = 0
	# for all the found releases
	for rel in rels:
		name, epoch, version, date, extra = rel
		
		# get the package id
		cur.execute("SELECT id FROM packages WHERE name=%s",(name,))
		row = cur.fetchone()
		if row:
			pkg_id = row[0]
		else:
			cur.execute("insert into packages (name) values (%s)",(name,))
			cur.execute("select last_insert_id();");
			pkg_id = cur.fetchone()[0]
		
		# store the release
		try:
			# make sure its not a duplicate
			cur.execute("select id from releases where package_id=%s and epoch=%s and version=%s and repo_id is null",(pkg_id,epoch,version))
			if cur.fetchone()!=None:
				continue
			cur.execute("insert into releases (package_id, epoch, version, released) values (%s,%s,%s,%s)",(pkg_id,epoch,version,date))
			count += 1
			cache.evict([(pkg_id, None)])
			if EXTRA and extra:
				cur.execute("select last_insert_id();")
				rel_id = cur.fetchone()[0]
				cur.execute("insert into extra (release_id, content) values (%s, %s)", (rel_id,extra))
		except mysql.IntegrityError:
			pass
	
	#print cpkg_i
	# update crawls
	if count>0:
		cur.execute("insert into crawls (package_id, release_count, time) values (%s,%s,NOW())", [cpkg_id,count])
	else:
		cur.execute("insert into crawls (package_id, time) values (%s,NOW())", [cpkg_id])
	
	con.commit()
	con.close()
	del cache
	print count,"releases"
	return count

print "Using %s/%s."%(HOST,DATABASE)
gc.enable()
stats = []

if "--ignore-last" in sys.argv:
	sys.argv.remove("--ignore-last")
	last = False
else:
	last = True

if len(sys.argv)>1:
	if "upstream" in sys.argv:
		sys.argv.remove("upstream")
		for u in UPSTREAM.keys():
			try:
				stats.append((u,UPSTREAM[u].crawl()))
			except:
				print "error from upstream:",u
				print traceback.format_exc()
			gc.collect()
	if "downstream" in sys.argv:
		sys.argv.remove("downstream")
		for d in DISTROS.keys():
			try:
				stats.append((d,DISTROS[d].crawl()))
			except:
				print "error from upstream:",d
				print traceback.format_exc()
			gc.collect()
	for crawl in sys.argv[1:]:
		if DISTROS.has_key(crawl):
			try:
				stats.append((crawl,DISTROS[crawl].crawl()))
			except:
				print "error from distro:",crawl
				print traceback.format_exc()
			gc.collect()
			continue
		if UPSTREAM.has_key(crawl):
			try:
				UPSTREAM[crawl].crawl()
			except:
				print "error from upstream:",crawl
				print traceback.format_exc()
			gc.collect()
			continue
		print "unknown",crawl
else:
	print "no args - running all"
	for d in DISTROS.keys():
		try:
			stats.append((d,DISTROS[d].crawl()))
		except:
			print "error from distro:",d
			print traceback.format_exc()
		gc.collect()
	for u in UPSTREAM.keys():
		try:
			stats.append((u,UPSTREAM[u].crawl()))
		except:
			print "error from upstream:",u
			print traceback.format_exc()
		gc.collect()

cache = Cache()
cache.evict([(None, None)])

save_to = open("crawl_stats/"+str(int(time.time()))+".pickle","w")
pickle.dump(stats,save_to)
save_to.close()

print "Done using %s/%s."%(HOST,DATABASE)
