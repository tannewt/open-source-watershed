import MySQLdb as mysql
import datetime
import sys
sys.path.append("")

#open the file
from utils import helper

HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
cur = con.cursor()

print "creating link_sources"
try:
	cur.execute("""CREATE TABLE link_sources (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
description TEXT
) ENGINE=INNODB""")
except:
	print "table exists"

print "creating links"
try:
	cur.execute("""CREATE TABLE links (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
link_source_id INT UNSIGNED,
package_id1 INT UNSIGNED,
distro_id1 INT UNSIGNED,
package_id2 INT UNSIGNED,
distro_id2 INT UNSIGNED,
strength TINYINT UNSIGNED DEFAULT 255,
FOREIGN KEY (link_source_id) REFERENCES link_sources(id) ON DELETE CASCADE,
FOREIGN KEY (package_id1) REFERENCES packages(id) ON DELETE CASCADE,
FOREIGN KEY (distro_id1) REFERENCES distros(id) ON DELETE CASCADE,
FOREIGN KEY (package_id2) REFERENCES packages(id) ON DELETE CASCADE,
FOREIGN KEY (distro_id2) REFERENCES distros(id) ON DELETE CASCADE
) ENGINE=INNODB""")
except:
	print "table exists"

print "adding 'by hand'"
#cur.execute("INSERT INTO link_sources (description) VALUES ('By hand.')")

print "adding 'Debian Source file'"
#cur.execute("INSERT INTO link_sources (description) VALUES ('Debian Source file.')")

con.commit()

cur.execute("SELECT source_id, id FROM packages WHERE source_id IS NOT NULL")
cur2 = con.cursor()
for row in cur:
	cur2.execute("INSERT INTO links (package_id1, package_id2, link_source_id, strength) VALUES (%s, %s, 6, 192)", row)

con.commit()
con.close()
