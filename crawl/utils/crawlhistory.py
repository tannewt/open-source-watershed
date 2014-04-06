# -*- coding: utf-8 -*-
import sys
import os
import psycopg2 as db
import datetime
import threading

sys.path.append(os.getcwd())
from utils import helper
from utils.cache import Cache
from utils.errors import *

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class CrawlHistory:
	def __init__(self,package=None,distro=None):
		c = Cache()
		self.releases = []
		
		con = db.connect(host=HOST,user=USER,password=PASSWORD,database=DB)
		cur = con.cursor()
		
		if package != None:
			cur.execute("SELECT id FROM packages WHERE name = %s",(package,))
			package_id = cur.fetchone()[0]
		else:
			package_id = None
		
		if distro != None:
			cur.execute("SELECT id FROM distros WHERE name = %s",(distro,))
			row = cur.fetchone()
			if row==None:
				print "Unknown distro: " + distro
				raise UnknownDistroError(distro)
			distro_id = row[0]
		else:
			distro_id = None
		
		cached = False
		if package == None and distro == None:
			key = "/upstream/latest"
			query = "SELECT packages.name, ureleases.version, MIN(ureleases.released) FROM packages, ureleases WHERE packages.id = ureleases.package_id GROUP BY packages.name, ureleases.version HAVING MIN(ureleases.released) >= current_timestamp - interval '1 day' ORDER BY MIN(ureleases.released) DESC, packages.name ASC LIMIT 100"
			query_args = []
		elif package == None and distro != None:
			key = "/distro/%s/latest"%distro
			query = "SELECT packages.name, dreleases.version, dreleases.revision, MIN(dreleases.released) FROM packages, dreleases, repos, distros WHERE packages.id = dreleases.package_id AND repos.id = dreleases.repo_id AND distros.id = repos.distro_id AND distros.name = %s GROUP BY packages.name, dreleases.version, dreleases.revision HAVING MIN(dreleases.released) >= current_timestamp - interval '1 day' ORDER BY MIN(dreleases.released) DESC, packages.name ASC LIMIT 100"
			query_args = (distro,)
		elif package != None and distro == None:
			key = "/pkg/%s/latest"%package
			query = "SELECT packages.name, ureleases.version, MIN(ureleases.released) FROM packages, ureleases WHERE packages.id = ureleases.package_id AND packages.name = %s GROUP BY packages.name, ureleases.version HAVING MIN(ureleases.released) >= current_timestamp - interval '1 day'ORDER BY MIN(ureleases.released) DESC LIMIT 100"
			query_args = (package,)
		else:
			key = "/distro/%s/pkg/%s/latest"%(distro,package)
			query = "SELECT packages.name, dreleases.version, dreleases.revision, MIN(dreleases.released) FROM packages, dreleases, repos, distros WHERE packages.id = dreleases.package_id AND repos.id = dreleases.repo_id AND distros.id = repos.distro_id AND distros.name = %s AND packages.name = %s GROUP BY packages.name, dreleases.version, dreleases.revision HAVING MIN(dreleases.released) >= current_timestamp - interval '1 day' ORDER BY MIN(dreleases.released) DESC LIMIT 100"
			query_args = (distro,package)
		
		now = datetime.datetime.now()
		day = datetime.timedelta(1)
		
		status = c.key_status(key)
		if status != None:
			self.releases = c.get(key)
			if status == Cache.STALE:
				t = threading.Thread(target=self.update, args=(key, query, query_args, package_id, distro_id))
				t.start()
		else:
			self.update(key, query, query_args, package_id, distro_id)
			
		self.today = len(self.releases)
	
	def update(self, key, query, query_args, package_id, distro_id, cache=None):
		if cache == None:
			cache = Cache()
		
		con = db.connect(host=HOST,user=USER,password=PASSWORD,database=DB)
		cur = con.cursor()
		
		cur.execute(query, query_args)
		
		tmp = []
		for row in cur:
			tmp.append(row)
		
		self.releases = tmp
		cache.put(key,tmp,[(package_id,distro_id)])
	
	def __str__(self):
		result = []
		for rel in self.releases:
			result.append(" ".join(map(str,rel)))
		return "\n".join(result)

if __name__=="__main__":
	print CrawlHistory()
	print
	print CrawlHistory("gcc")
	print
	print CrawlHistory(None,"gentoo")
	print
	print CrawlHistory("inkscape","gentoo")
