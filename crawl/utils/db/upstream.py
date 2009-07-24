# -*- coding: utf-8 -*-
from . import cursor
from . import core
import psycopg2

def source(name, description, user_id=1):
	with cursor() as cur:
		cur.execute("SELECT id FROM usources WHERE name = %s AND user_id = %s", (name, user_id))
		row = cur.fetchone()
		
		if row == None:
			cur.execute("INSERT INTO usources (name, description, user_id) VALUES (%s, %s, %s)", (name, description, user_id))
			cur.execute("SELECT lastval()")
			i = cur.fetchone()[0]
		else:
			i = row[0]
	
	return i

def add_releases(source_id, rels, test, cache=None):
	pkgs = {}
	max_date = None
	for rel in rels:
		if max_date==None or max_date < rel.released:
			max_date = rel.released
		if rel.package in pkgs:
			rel.package = pkgs[rel.package]
		else:
			rel.package = core.package(rel.package)
	
	total_new = 0
	with cursor() as cur:
		if test:
			for rel in rels:
				cur.execute("SELECT id FROM ureleases WHERE package_id = %s AND version = %s AND revision = %s AND usource_id = %s",(rel.package, rel.version, rel.revision, source_id))
				if cur.fetchone()==None:
					print "new", rel
					total_new += 1
		else:
			for rel in rels:
				try:
					cur.execute("INSERT INTO ureleases (package_id, version, released, usource_id) VALUES (%s, %s, %s, %s)",(rel.package, rel.version, rel.released, source_id))
					if cache != None:
						cache.evict([(rel.package, None)])
					total_new += 1
				except psycopg2.IntegrityError:
					pass
	return (total_new, max_date)
	
def last_crawl(source_id):
	with cursor() as cur:
		cur.execute("SELECT last_crawl FROM usources WHERE id = %s",(source_id,))
		last_crawl = cur.fetchone()[0]
	return last_crawl

def set_last_crawl(source_id, last_crawl, test):
	if test:
		return
	with cursor() as cur:
		cur.execute("UPDATE usources SET last_crawl = %s WHERE id = %s",(last_crawl, source_id))