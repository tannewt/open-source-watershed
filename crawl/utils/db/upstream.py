# -*- coding: utf-8 -*-
from . import db, get_cursor, close_cursor, commit
from . import core

def source(name, description, user_id=1):
	cur = get_cursor()
	cur.execute("SELECT id FROM usources WHERE name = %s AND user_id = %s", (name, user_id))
	row = cur.fetchone()
	
	if row == None:
		print "try insert source:",name
		cur.execute("INSERT INTO usources (name, description, user_id) VALUES (%s, %s, %s)", (name, description, user_id))
		cur.execute("SELECT lastval()")
		i = cur.fetchone()[0]
	else:
		i = row[0]
	close_cursor(cur)
	
	return i

def add_releases(source_id, rels):
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
	cur = get_cursor()
	for rel in rels:
		try:
			cur.execute("INSERT INTO ureleases (package_id, version, released, usource_id) VALUES (%s, %s, %s, %s)",(rel.package, rel.version, rel.released, source_id))
			total_new += 1
		except db.IntegrityError:
			pass
		commit()
	close_cursor(cur)
	return (total_new, max_date)
	
def last_crawl(source_id):
	cur = get_cursor()
	cur.execute("SELECT last_crawl FROM usources WHERE id = %s",(source_id,))
	last_crawl = cur.fetchone()[0]
	close_cursor(cur)
	return last_crawl

def set_last_crawl(source_id, last_crawl):
	cur = get_cursor()
	cur.execute("UPDATE usources SET last_crawl = %s WHERE id = %s",(last_crawl, source_id))
	close_cursor(cur)