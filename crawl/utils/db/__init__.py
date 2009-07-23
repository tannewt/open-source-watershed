# -*- coding: utf-8 -*-
import psycopg2 as db
from psycopg2 import pool
from contextlib import contextmanager

#open the file
from .. import helper
HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
pool = pool.ThreadedConnectionPool(2,10,host=HOST, user=USER, password=PASSWORD, database=DATABASE)

@contextmanager
def cursor():
	global pool
	con = pool.getconn()
	try:
		yield con.cursor()
	finally:
		con.commit()
		pool.putconn(con)