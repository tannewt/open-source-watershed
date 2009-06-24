# -*- coding: utf-8 -*-
import psycopg2 as db

#open the file
from .. import helper
HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = None
refcount = 0

# Not threadsafe!
def get_cursor():
	global con
	global refcount
	if con==None:
		con = db.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
	refcount += 1
	return con.cursor()

def close_cursor(cur):
	global con
	global refcount
	cur.close()
	con.commit()
	refcount -= 1
	if refcount==0:
		con.close()
		con = None

def commit():
	con.commit()