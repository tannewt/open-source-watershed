# -*- coding: utf-8 -*-
from . import db, get_cursor, close_cursor, commit
from . import core

def distro(name, color=None, description=None, website=None):
	cur = get_cursor()
	cur.execute("SELECT id FROM distros WHERE name = %s", (name,))
	row = cur.fetchone()
	
	if row == None:
		cur.execute("INSERT INTO distros (name, color, description, website) VALUES (%s, %s, %s, %s)", (name, color, description, website))
		cur.execute("SELECT lastval()")
		row = cur.fetchone()
	i = row[0]
	close_cursor(cur)
	return i

def repo(repo, test):
	cur = get_cursor()
	cur.execute("SELECT id, last_crawl FROM repos WHERE distro_id = %s AND codename = %s AND component = %s AND architecture = %s", (repo.distro_id, repo.codename, repo.component, repo.architecture))
	row = cur.fetchone()
	if row == None:
		cur.execute("INSERT INTO repos (distro_id, codename, component, architecture) VALUES (%s, %s, %s, %s)", (repo.distro_id, repo.codename, repo.component, repo.architecture))
		cur.execute("SELECT lastval()")
		repo.id = cur.fetchone()[0]
		if test:
			print "new repo, id:",repo.id,"-",repo
	else:
		repo.id, repo.last_crawl = row
	close_cursor(cur)

def add_branch(repo, branch, test):
	cur = get_cursor()
	cur.execute("SELECT id FROM branches WHERE repo_id = %s AND branch = %s", (repo.id, branch))
	row = cur.fetchone()
	
	if row == None:
		cur.execute("INSERT INTO branches (repo_id, branch, start) VALUES (%s, %s, NOW())", (repo.id, branch))
		cur.execute("SELECT lastval()")
		i = cur.fetchone()[0]
		if test:
			print "new branch, id:", i, "-", branch
	close_cursor(cur)

def add_releases(repo, rels, test=False, cache=None):
	pkgs = {}
	for rel in rels:
		if rel.package in pkgs:
			rel.package = pkgs[rel.package]
		else:
			rel.package = core.package(rel.package, test)
	
	total_new = 0
	cur = get_cursor()
	if test:
		for rel in rels:
			cur.execute("SELECT id FROM dreleases WHERE package_id = %s AND version = %s AND revision = %s AND repo_id = %s",(rel.package, rel.version, rel.revision, repo.id))
			if cur.fetchone()==None:
				print "new", rel
				total_new += 1
	else:
		for rel in rels:
			try:
				cur.execute("INSERT INTO dreleases (package_id, version, revision, released, repo_id) VALUES (%s, %s, %s, %s, %s)",(rel.package, rel.version, rel.revision, rel.released, repo.id))
				if cache!=None:
					cache.evict([(rel.package, repo.distro_id)])
				total_new += 1
			except db.IntegrityError:
				pass
			commit()
	close_cursor(cur)
	return total_new

def set_last_crawl(repo, last_crawl, test):
	if test:
		return
	if last_crawl==None:
		print "WARNING! Setting last_crawl to None."
	cur = get_cursor()
	cur.execute("UPDATE repos SET last_crawl = %s WHERE id = %s",(last_crawl, repo.id))
	close_cursor(cur)