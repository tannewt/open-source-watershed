# -*- coding: utf-8 -*-
from . import get_cursor, close_cursor, commit, db
from . import core

def add_sf_target(name, project_num, packages, bad_tokens, bad_versions, user_id=1):
	cur = get_cursor()
	cur.execute("INSERT INTO sf (name, project_num, packages, bad_tokens, bad_versions, user_id) VALUES (%s, %s, %s, %s, %s, %s)",(name, project_num, packages, bad_tokens, bad_versions, user_id))
	cur.execute("SELECT lastval();")
	i = cur.fetchone()[0]
	close_cursor(cur)
	return i

def get_sf_target(name):
	cur = get_cursor()
	cur.execute("SELECT id, name, project_num, packages, bad_tokens, bad_versions, last_crawl FROM sf WHERE name = %s", (name,))
	row = cur.fetchone()
	close_cursor(cur)
	return row

def get_sf_targets():
	cur = get_cursor()
	cur.execute("SELECT name, project_num, packages, bad_tokens, bad_versions, last_crawl FROM sf")
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
	for rel in rels:
		if max_date==None or max_date < rel.released:
			max_date = rel.released
		
		try:
			cur.execute("INSERT INTO ureleases (package_id, version, released, usource_id) VALUES (%s, %s, %s, %s)",(rel.package, rel.version, rel.released, source_id))
			cur.execute("SELECT lastval()")
			i = cur.fetchone()[0]
			cur.execute("INSERT INTO sf_releases (sf_id, urelease_id) VALUES (%s, %s)", (target_id, i))
			total_new += 1
		except db.IntegrityError:
			pass
		commit()
	close_cursor(cur)
	return (total_new, max_date)

def last_crawl(target_id):
	cur = get_cursor()
	cur.execute("SELECT last_crawl FROM sf WHERE id = %s",(target_id,))
	last_crawl = cur.fetchone()[0]
	close_cursor(cur)
	return last_crawl

def set_last_crawl(target_id, last_crawl):
	cur = get_cursor()
	cur.execute("UPDATE sf SET last_crawl = %s WHERE id = %s",(last_crawl, target_id))
	close_cursor(cur)