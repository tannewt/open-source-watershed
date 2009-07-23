# -*- coding: utf-8 -*-
from . import cursor
from . import core
import psycopg2

def add_explore_target(name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id=1):
	with cursor() as cur:
		cur.execute("INSERT INTO explore (name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",(name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, user_id))
		cur.execute("SELECT lastval();")
		i = cur.fetchone()[0]
	return i

def get_explore_target(name):
	with cursor() as cur:
		cur.execute("SELECT id, name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, last_crawl FROM explore WHERE name = %s", (name,))
		row = cur.fetchone()
	return row

def get_explore_targets():
	with cursor() as cur:
		cur.execute("SELECT id, name, url, target_depth, good_packages, bad_packages, bad_tokens, bad_versions, deadends, last_crawl FROM explore")
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
					cur.execute("INSERT INTO explore_releases (explore_id, urelease_id) VALUES (%s, %s)", (target_id, i))
					if cache!=None:
						cache.evict([(rel.package, None)])
					total_new += 1
				except psycopg2.IntegrityError:
					pass
	return (total_new, max_date)

def last_crawl(target_id):
	with cursor() as cur:
		cur.execute("SELECT last_crawl FROM explore WHERE id = %s",(target_id,))
		last_crawl = cur.fetchone()[0]
	return last_crawl

def set_last_crawl(target_id, last_crawl, test):
	if test:
		return
	with cursor() as cur:
		cur.execute("UPDATE explore SET last_crawl = %s WHERE id = %s",(last_crawl, target_id))