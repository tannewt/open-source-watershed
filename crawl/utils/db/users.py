# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
from utils import types
import random

def create(username, passwd, email):
	with cursor() as cur:
		cur.execute("INSERT INTO users (handle, pswhash, email, joined) VALUES (%s, crypt(%s, gen_salt('md5')), %s, now())",(username, passwd, email))
		cur.execute("SELECT lastval();")
		i = cur.fetchone()[0]
	return i

def get(username, passwd):
	with cursor() as cur:
		cur.execute("SELECT * FROM users WHERE handle = %s AND pswhash = crypt(%s, pswhash)",(username, passwd))
		if cur.rowcount > 0:
			user = types.User()
			user.username = username
			return user
		else:
			return None
	return None