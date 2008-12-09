import MySQLdb as mysql

con = mysql.connect(host="localhost",user="root",passwd="hello",db="rev2")

# patterns fixed:
# %.dfsg.%
# %dfsg
# %~dfsg%
# %.dfsg%

cur = con.cursor()
cur.execute("SELECT releases.id, releases.version, releases.revision FROM releases WHERE releases.version LIKE '%dfsg%'")

cur2 = con.cursor()
for id, ver, rev in cur:
  #print id,ver,rev,"=>",
  ver, g_rev = ver.rsplit("dfsg",1)
  rev = g_rev + "." + rev
  if not ver[-1].isdigit():
    ver = ver[:-1]
  if not (rev[0].isdigit() or rev[0].isalpha()):
    rev = rev[1:]
  #print ver,rev
  cur2.execute("UPDATE releases SET version=%s, revision=%s WHERE id=%s",(ver,rev,id))
  #cur2.execute("UPDATE releases SET version=%s WHERE id=%s",(ver[:-4],id))
con.commit()
con.close()
