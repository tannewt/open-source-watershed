# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
from . import core
import psycopg2

def add_sf_target(name, project_num, packages, bad_tokens, bad_versions, user_id=1):
	with cursor() as cur:
		cur.execute("INSERT INTO sf (name, project_num, packages, bad_tokens, bad_versions, user_id) VALUES (%s, %s, %s, %s, %s, %s)",(name, project_num, packages, bad_tokens, bad_versions, user_id))
		cur.execute("SELECT lastval();")
		i = cur.fetchone()[0]
	return i

def get_sf_target(name):
	with cursor() as cur:
		cur.execute("SELECT id, name, project_num, packages, bad_tokens, bad_versions, last_crawl FROM sf WHERE name = %s", (name,))
		row = cur.fetchone()
	return row

def get_sf_targets():
	with cursor() as cur:
		cur.execute("SELECT id, name, project_num, packages, bad_tokens, bad_versions, last_crawl FROM sf")
		result = []
		for row in cur:
			result.append(row)
	return result

def add_releases(source_id, target_id, rels, test, cache=None):
	pkgs = {}
	for rel in rels:
		if rel.package in pkgs:
			rel.package = pkgs[rel.package]
		else:
			rel.package = core.package(rel.package)
	
	total_new = 0
	max_date = None
	if test:
		for rel in rels:
			with cursor() as cur:
				cur.execute("SELECT id FROM ureleases WHERE package_id = %s AND version = %s AND revision = %s AND usource_id = %s",(rel.package, rel.version, rel.revision, source_id))
				if cur.fetchone()==None:
					print "new", rel
					total_new += 1
	else:
		for rel in rels:
			if max_date==None or max_date < rel.released:
				max_date = rel.released
			
			with cursor() as cur:
				try:
					cur.execute("INSERT INTO ureleases (package_id, version, released, usource_id) VALUES (%s, %s, %s, %s)",(rel.package, rel.version, rel.released, source_id))
					cur.execute("SELECT lastval()")
					i = cur.fetchone()[0]
					cur.execute("INSERT INTO sf_releases (sf_id, urelease_id) VALUES (%s, %s)", (target_id, i))
					if cache!=None:
						cache.evict([(rel.package, None)])
					total_new += 1
				except psycopg2.IntegrityError:
					pass
	return (total_new, max_date)

def last_crawl(target_id):
	with cursor() as cur:
		cur.execute("SELECT last_crawl FROM sf WHERE id = %s",(target_id,))
		last_crawl = cur.fetchone()[0]
	return last_crawl

def set_last_crawl(target_id, last_crawl, test):
	if test:
		return
	with cursor() as cur:
		cur.execute("UPDATE sf SET last_crawl = %s WHERE id = %s",(last_crawl, target_id))