# -*- coding: utf-8 -*-
from . import get_cursor, close_cursor
import random

def create(handle, passwd, email):
	cur = get_cursor()
	cur.execute("INSERT INTO users (handle, pswhash, email, joined) VALUES (%s, crypt(%s, gen_salt('md5')), %s, now())",(handle, passwd, email))
	cur.execute("SELECT lastval();")
	i = cur.fetchone()[0]
	close_cursor(cur)
	return i