# -*- coding: utf-8 -*-
from __future__ import with_statement

from . import cursor
import random

def create(handle, passwd, email):
	with cursor() as cur:
		cur.execute("INSERT INTO users (handle, pswhash, email, joined) VALUES (%s, crypt(%s, gen_salt('md5')), %s, now())",(handle, passwd, email))
		cur.execute("SELECT lastval();")
		i = cur.fetchone()[0]
	return i