# -*- coding: utf-8 -*-
from . import get_cursor, close_cursor, commit, db
from . import core

def add_explore_target(name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id=1):
	cur = get_cursor()
	cur.execute("INSERT INTO explore (name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",(name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id))
	cur.execute("SELECT lastval();")
	i = cur.fetchone()[0]
	close_cursor(cur)
	return i

def get_explore_target(name):
	cur = get_cursor()
	cur.execute("SELECT id, name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, last_crawl FROM explore WHERE name = %s", (name,))
	row = cur.fetchone()
	close_cursor(cur)
	return row

def get_explore_targets():
	cur = get_cursor()
	cur.execute("SELECT id, name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, last_crawl FROM explore")
	result = []
	for row in cur:
	 result.append(row)
	close_cursor(cur)
	return result

def add_releases(source_id, target_id, rels):
	pkgs = {}
	for rel in rels:
		if rel.package in pkgs:
			rel.package = pkgs[rel.package]
		else:
			rel.package = core.package(rel.package)
	
	total_new = 0
	cur = get_cursor()
	max_date = None
	if test:
		for rel in rels:
			cur.execute("SELECT id FROM ureleases WHERE package_id = %s AND version = %s AND revision = %s AND usource_id = %s",(rel.package, rel.version, rel.revision, source_id))
			if cur.fetchone()==None:
				print "new", rel
				total_new += 1
	else:
		for rel in rels:
			if max_date==None or max_date < rel.released:
				max_date = rel.released
			
			try:
				cur.execute("INSERT INTO ureleases (package_id, version, released, usource_id) VALUES (%s, %s, %s, %s)",(rel.package, rel.version, rel.released, source_id))
				cur.execute("SELECT lastval()")
				i = cur.fetchone()[0]
				cur.execute("INSERT INTO explore_releases (explore_id, urelease_id) VALUES (%s, %s)", (target_id, i))
				total_new += 1
			except db.IntegrityError:
				pass
			commit()
	close_cursor(cur)
	return (total_new, max_date)

def last_crawl(target_id):
	cur = get_cursor()
	cur.execute("SELECT last_crawl FROM explore WHERE id = %s",(target_id,))
	last_crawl = cur.fetchone()[0]
	close_cursor(cur)
	return last_crawl

def set_last_crawl(target_id, last_crawl, test):
	if test:
		return
	cur = get_cursor()
	cur.execute("UPDATE explore SET last_crawl = %s WHERE id = %s",(last_crawl, target_id))
	close_cursor(cur)