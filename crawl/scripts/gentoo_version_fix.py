import MySQLdb as mysql

con = mysql.connect(host="localhost",user="root",passwd="hello",db="rev2")

cur = con.cursor()
cur.execute("SELECT releases.id, releases.version FROM releases, repos, distros WHERE releases.repo_id = repos.id AND repos.distro_id = distros.id AND distros.name='gentoo'")

cur2 = con.cursor()
for row in cur:
  cur2.execute("UPDATE releases SET version=%s WHERE id=%s",(row[1].strip("-"),row[0]))
con.commit()
con.close()
