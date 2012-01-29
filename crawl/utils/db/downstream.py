# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
from . import core
import psycopg2

def list_distros():
	with cursor() as cur:
		cur.execute("SELECT name FROM distros")
		result = map(lambda x: x[0], cur.fetchall())
	return result

def list_all_distro_packages(distro):
	with cursor() as cur:
		cur.execute("SELECT DISTINCT packages.name FROM packages, distros, repos, dreleases WHERE packages.id = dreleases.package_id AND distros.id=repos.distro_id AND repos.id = dreleases.repo_id AND distros.name=%s",(distro,))
		result = map(lambda x: x[0], cur.fetchall())
	return result

def distro(name, color=None, description=None, website=None):
	with cursor() as cur:
		cur.execute("SELECT id FROM distros WHERE name = %s", (name,))
		row = cur.fetchone()
		
		if row == None:
			cur.execute("INSERT INTO distros (name, color, description, website) VALUES (%s, %s, %s, %s)", (name, color, description, website))
			cur.execute("SELECT lastval()")
			row = cur.fetchone()
		i = row[0]
	return i

def repo(repo, test):
	with cursor() as cur:
		cur.execute("SELECT id, last_crawl FROM repos WHERE distro_id = %s AND codename = %s AND component = %s AND architecture = %s", (repo.distro_id, str(repo.codename), str(repo.component), str(repo.architecture)))
		row = cur.fetchone()
		if row == None:
			cur.execute("INSERT INTO repos (distro_id, codename, component, architecture) VALUES (%s, '%s', '%s', '%s')", (repo.distro_id, str(repo.codename), str(repo.component), str(repo.architecture)))
			cur.execute("SELECT lastval()")
			repo.id = cur.fetchone()[0]
			if test:
				print "new repo, id:",repo.id,"-",repo
		else:
			repo.id, repo.last_crawl = row

def add_branch(repo, branch, test):
	with cursor() as cur:
		cur.execute("SELECT id FROM branches WHERE repo_id = %s AND branch = %s", (repo.id, branch))
		row = cur.fetchone()
		
		if row == None:
			cur.execute("INSERT INTO branches (repo_id, branch, start) VALUES (%s, %s, NOW())", (repo.id, branch))
			cur.execute("SELECT lastval()")
			i = cur.fetchone()[0]
			if test:
				print "new branch, id:", i, "-", branch

def add_releases(repo, rels, test=False, cache=None):
	pkgs = {}
	for rel in rels:
		if rel.package in pkgs:
			rel.package = pkgs[rel.package]
		else:
			rel.package = core.package(rel.package, test)
	
	total_new = 0
	
	for rel in rels:
		with cursor() as cur:
			cur.execute("SELECT id FROM dreleases WHERE package_id = %s AND version = %s AND revision = %s AND repo_id = %s",(rel.package, rel.version, rel.revision, repo.id))
			if cur.fetchone() != None:
				continue
			if test:
				print "new", rel
				continue
			total_new += 1
			cur.execute("INSERT INTO dreleases (package_id, version, revision, released, repo_id) VALUES (%s, %s, %s, %s, %s)",(rel.package, rel.version, rel.revision, rel.released, repo.id))
			if cache != None:
				cache.evict([(rel.package, repo.distro_id)])
	return total_new

def set_last_crawl(repo, last_crawl, test):
	if test:
		return
	if last_crawl==None:
		print "WARNING! Setting last_crawl to None."
	with cursor() as cur:
		cur.execute("UPDATE repos SET last_crawl = %s WHERE id = %s",(last_crawl, repo.id))
