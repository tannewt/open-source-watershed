# -*- coding: utf-8 -*-
import psycopg2 as db
from psycopg2 import pool
from psycopg2 import extensions
from contextlib import contextmanager

#open the file
from .. import helper
HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
pool = pool.ThreadedConnectionPool(2,50,host=HOST, user=USER, password=PASSWORD, database=DATABASE)

@contextmanager
def cursor():
	global pool
	con = pool.getconn()
	con.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	try:
		yield con.cursor()
	finally:
		con.commit()
		pool.putconn(con)
