# -*- coding: utf-8 -*-
from . import db, get_cursor, close_cursor
import random

def package(p):
	cur = get_cursor()
	i = None
	cur.execute("select id from packages where name=%s", (p,))
	row = cur.fetchone()
	if row==None:
		cur.execute("insert into packages(name) values (%s);",(p,))
		cur.execute("select lastval();");
		i = cur.fetchone()[0]
	else:
		i = row[0]
	
	close_cursor(cur)
	return i

def distro(distro):
	cur = get_cursor()
	i = None
	try:
		cur.execute("insert into distros(name) values (%s);",distro)
		cur.execute("select lastval();");
		i = cur.fetchone()[0]
	except db.IntegrityError:
		#print "found"
		cur.execute("select id from distros where name=%s", distro)
		i = cur.fetchone()[0]
	finally:
		close_cursor(cur)
	return i

def get_downstream_releases(distro_id, packages, branch, revisions):
	if revisions:
		rev = ", revision"
	else:
		rev = ""
	
	q = "SELECT version"+rev+", MIN(released) FROM ( SELECT version"+rev+", GREATEST(released, start) AS released FROM dreleases, repos, branches WHERE ("+ " OR ".join(("dreleases.package_id=%s",)*len(packages)) + ") AND dreleases.repo_id=repos.id AND repos.distro_id=%s AND dreleases.version!='9999' AND repos.id = branches.repo_id AND branches.branch = %s) t GROUP BY version"+rev+" ORDER BY MIN(released), version"+rev
	
	cur = get_cursor()
	cur.execute(q,packages+[distro_id, branch])
	releases = []
	for row in cur:
		releases.append(tuple(row))
	close_cursor(cur)
	return releases