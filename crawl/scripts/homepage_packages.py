import sys

if len(sys.argv)<2:
  print "wrong"
  sys.exit(1)

def url_parse(page):
  if page.startswith("http://"):
    page = page[7:]
  if page.startswith("ftp://"):
    page = page[6:]
  if page.startswith("www."):
    page = page[4:]
  if page[-1]=="/":
    page = page[:-1]
  
  bits = page.split("/")
  domain = bits[0].split(".")
  domain.reverse()
  return domain+bits[1:]
    
f = open(sys.argv[1])
rev = {}
for line in f:
  try:
    package, page = line.strip().split(None,1)
  except:
    print "bad: " + line.strip()
    continue
  
  page = url_parse(page)
  if "" in page:
    continue
  cur = rev
  for bit in page:
    if bit not in cur:
      cur[bit] = {"":[]}
    cur = cur[bit]
  if package not in cur[""]:
    cur[""].append(package)

f.close()

import MySQLdb as mysql
import sys
import os

sys.path.append(os.getcwd())
from utils import helper

import gtk

HOST, USER, PASSWORD, DB = helper.mysql_settings()
con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
cur = con.cursor()

def to_source(name):
  cur.execute("SELECT name,id,source_id FROM packages WHERE name = %s",(name,))
  row = cur.fetchone()
  return row

def fill(store, parent, data):
  keys = data.keys()
  keys.sort()
  for key in keys:
    if key!="":
      new = store.append(parent, ("<b>"+key+"</b> "+str(len(data[key])),"",""))
      fill(store, new, data[key])
  if "" in data:
    data[""].sort()
    for v in data[""]:
      store.append(parent, to_source(v))

window = gtk.Window()
sc = gtk.ScrolledWindow()
treeview = gtk.TreeView()
treestore = gtk.TreeStore(str,str,str)
fill(treestore, None, rev)
renderer = gtk.CellRendererText()
col = gtk.TreeViewColumn("name", renderer, markup=0)
treeview.append_column(col)
col = gtk.TreeViewColumn("id", renderer, markup=1)
treeview.append_column(col)
col = gtk.TreeViewColumn("source", renderer, markup=2)
treeview.append_column(col)

treeview.set_model(treestore)
sc.add(treeview)
window.add(sc)
window.show_all()

window.connect("destroy",lambda x: gtk.main_quit())
gtk.main()
