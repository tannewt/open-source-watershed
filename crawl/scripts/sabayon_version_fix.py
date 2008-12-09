import MySQLdb as mysql

con = mysql.connect(host="localhost",user="root",passwd="hello",db="rev2")

cur = con.cursor()
cur.execute("SELECT releases.id, releases.version, releases.revision FROM releases, repos, distros WHERE releases.repo_id = repos.id AND repos.distro_id = distros.id AND distros.name='sabayon'")

cur2 = con.cursor()
for id, ver, rev in cur:
  if len(ver)>3 and ver[-3]=="-":
    ver, g_rev = ver.rsplit("-")
    rev = g_rev[1:] + "." + rev
    cur2.execute("UPDATE releases SET version=%s, revision=%s WHERE id=%s",(ver,rev,id))
con.commit()
con.close()
