# -*- coding: utf-8 -*-
from . import db, get_cursor, close_cursor
import random

def package(p):
	cur = get_cursor()
	i = None
	cur.execute("select id from packages where name=%s", (p,))
	row = cur.fetchone()
	if row==None:
		print "insert package",p
		cur.execute("insert into packages(name) values (%s);",(p,))
		cur.execute("select lastval();");
		i = cur.fetchone()[0]
	else:
		i = row[0]
	
	close_cursor(cur)
	return i

def repo(repo):
	pass

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