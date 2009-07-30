# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
import random
import threading

def package(p, test=False):
	with cursor() as cur:
		i = None
		cur.execute("select id from packages where name=%s", (p,))
		row = cur.fetchone()
		if row==None and not test:
			cur.execute("insert into packages(name) values (%s);",(p,))
			cur.execute("select lastval();");
			i = cur.fetchone()[0]
		elif row==None:
			print "new package:",p
		else:
			i = row[0]
	return i

def distro(distro):
	i = None
	with cursor() as cur:
		try:
			cur.execute("insert into distros(name) values (%s);",distro)
			cur.execute("select lastval();");
			i = cur.fetchone()[0]
		except db.IntegrityError:
			#print "found"
			cur.execute("select id from distros where name=%s", distro)
			i = cur.fetchone()[0]
	return i

def get_downstream_releases(distro_id, packages, branch, revisions):
	if revisions:
		rev = ", revision"
	else:
		rev = ""
	
	q = "SELECT version"+rev+", MIN(released) FROM ( SELECT version"+rev+", GREATEST(released, start) AS released FROM dreleases, repos, branches WHERE ("+ " OR ".join(("dreleases.package_id=%s",)*len(packages)) + ") AND dreleases.repo_id=repos.id AND repos.distro_id=%s AND dreleases.version!='9999' AND repos.id = branches.repo_id AND branches.branch = %s) t GROUP BY version"+rev+" ORDER BY MIN(released), version"+rev
	
	with cursor() as cur:
		cur.execute(q,packages+[distro_id, branch])
		releases = []
		for row in cur:
			releases.append(tuple(row))
	return releases

def get_all_distros():
	with cursor() as cur:
		cur.execute("SELECT name FROM distros ORDER BY name")
		distros = []
		for row in cur:
			distros.append(row[0])
	return distros