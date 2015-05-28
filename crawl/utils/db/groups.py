# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
#cur.execute("""CREATE TABLE groups (
#id SERIAL NOT NULL PRIMARY KEY,
#user_id INT NOT NULL REFERENCES users(id),
#name VARCHAR(255),
#UNIQUE (user_id, name)
#)""")

#cur.execute("""CREATE TABLE group_packages (
#group_id INT REFERENCES groups(id),
#package_id INT REFERENCES packages(id)
#)""")

def list_groups(user_id=1):
	with cursor() as cur:
		cur.execute("SELECT id,name FROM groups WHERE user_id = %s", (user_id,))
		result = cur.fetchall()
	return result

def create_group(name, user_id=1):
	with cursor() as cur:
		cur.execute("INSERT INTO groups (name, user_id) VALUES (%s, %s)", (name, user_id))
		cur.execute("SELECT lastval()")
		i = cur.fetchone()[0]
	return i

def delete_group(name, user_id=1):
	with cursor() as cur:
		cur.execute("DELETE FROM groups WHERE name=%s AND user_id = %s", (name,user_id))

def get_group(name, user_id=1):
	with cursor() as cur:
		cur.execute("SELECT packages.name FROM group_packages, groups, packages WHERE packages.id = group_packages.package_id AND groups.name = %s AND groups.user_id = %s", (name,user_id))
		result = map(lambda x: x[0], cur.fetchall())
		result.sort()
	return result

def add_to_group(pkg, name, user_id=1):
	with cursor() as cur:
		if type(pkg)!=int:
			cur.execute("SELECT id FROM packages WHERE name = %s",(pkg,))
			pkg = cur.fetchone()[0]
		cur.execute("INSERT INTO group_packages (package_id, group_id) SELECT %s, id FROM groups WHERE name=%s AND user_id = %s", (pkg,name,user_id))
	
def remove_from_group(pkg, name, user_id=1):
	with cursor() as cur:
            if type(pkg)!=int:
                cur.execute("SELECT id FROM packages WHERE name = %s",(pkg,))
                pkg = cur.fetchone()[0]
	    cur.execute("DELETE FROM group_packages WHERE package_id = %s AND group_id = (SELECT id FROM groups WHERE name=%s AND user_id = %s)", (pkg,name,user_id))
