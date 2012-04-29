import time
import datetime
import os
import urllib
import bz2
import sys

sys.path.append(os.getcwd())

from utils import helper,deb
from utils.db import core
from utils.db import cursor
MIRROR = "ubuntu.osuosl.org"

FTP_START_DIR = "pub/ubuntu/dists/"

HTTP_START_DIR = "ubuntu/dists/"

HOST, USER, PASSWORD, DB = helper.mysql_settings()

with cursor() as cur:
	total_bin = 0
	for comp in ["main","multiverse","restricted","universe"]:
		url = "http://" + MIRROR + "/" + HTTP_START_DIR + "precise/" + comp + "/source/Sources.bz2"
		filename = "files/ubuntu/Sources-precise-" + comp + "-" + str(time.time()) + ".bz2"

		info = helper.open_url(url, filename)
		f = bz2.BZ2File(filename)
		pkgs = deb.parse_package_dict(f)

		for p in pkgs:
			if not p.has_key("Package") or not p.has_key("Binary"):
				continue
			binaries = p["Binary"].split(", ")
			upstream = p["Package"]
			if upstream in binaries:
				binaries.remove(upstream)
			total_bin += len(binaries)
			print upstream, "=>", binaries
			package_tgt = core.package(upstream)
			if "Homepage" in p:
				cur.execute("select id from package_info where package_id=%s", (package_tgt,))
				row = cur.fetchone()
				if row==None:
					cur.execute("insert into package_info (package_id, homepage, user_id, _when) VALUES (%s, %s, 1, NOW())", (package_tgt, p["Homepage"]))
				else:
					cur.execute("update package_info set homepage=%s where package_id=%s", (p["Homepage"], row[0]))
			for binary in binaries:
				package_src = core.package(binary)
				cur.execute("INSERT INTO links (package_tgt, package_src, distro_src) VALUES (%s,%s,(SELECT id FROM distros WHERE name=%s))",(package_tgt,package_src,"ubuntu"))
print total_bin, "binaries"
