import MySQLdb as mysql
from utils import helper

HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD)
cur = con.cursor()

cur.execute('use '+DATABASE);

# every distro
cur.execute("SELECT id,repo_id FROM crawls")
cur2 = con.cursor()
for row in cur:
  print row
  cur2.execute("SELECT COUNT(*) FROM releases WHERE repo_id=%s",(row[1],))
  rels = cur2.fetchone()
  print row, rels
  cur2.execute("UPDATE crawls SET crawls.release_count=%s WHERE id=%s",(rels[0],row[0]))
con.commit()
con.close()
