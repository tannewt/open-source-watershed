import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())

from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)

import gtk,gobject
from utils import chart

class AgeView:
  def __init__(self):
    self.window = gtk.Window()
    self.window.set_default_size(500,300)
    self.window.show()

    hbox = gtk.HPaned()
    hbox.show()

    vbox = gtk.VBox()
    vbox.show()
    self.distro_store = gtk.ListStore(gobject.TYPE_STRING,gtk.gdk.Color)
    l = gtk.TreeView(self.distro_store)
    renderer = gtk.CellRendererText()
    l.append_column(gtk.TreeViewColumn("",renderer,text=0,foreground_gdk=1))
    l.show()
    vbox.add(l)
    
    # add distro stuff
    h = gtk.HBox()
    self.distro = gtk.combo_box_new_text()
    h.add(self.distro)
    self.branch = gtk.combo_box_new_text()
    h.add(self.branch)
    self.arch = gtk.combo_box_new_text()
    h.add(self.arch)
    self.color = gtk.ColorButton()
    h.add(self.color)
    self.add = gtk.Button(stock=gtk.STOCK_ADD)
    self.add.connect("clicked",self.add_distro)
    h.add(self.add)
    h.show_all()
    vbox.pack_start(h,False,False)
    
    # package stuff
    self.pkg_store = gtk.ListStore(gobject.TYPE_STRING)
    self.packages = []
    l = gtk.TreeView(self.pkg_store)
    renderer = gtk.CellRendererText()
    l.append_column(gtk.TreeViewColumn("",renderer,text=0))
    l.show()
    vbox.add(l)
    
    # add distro stuff
    h = gtk.HBox()
    self.pkg = gtk.Entry()
    h.add(self.pkg)
    self.add = gtk.Button(stock=gtk.STOCK_ADD)
    self.add.connect("clicked",self.add_pkg)
    h.add(self.add)
    h.show_all()
    vbox.pack_start(h,False,False)
    hbox.add(vbox)
    

    self.graph = chart.LineChart()

    hbox.add(self.graph)
    self.graph.show()
    self.window.add(hbox)
    self.window.connect("destroy",lambda x: gtk.main_quit())
    
    HOST, USER, PASSWORD, DB = helper.mysql_settings()

    self.con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    
    self.distros = {}
    cur = self.con.cursor()
    cur.execute("SELECT DISTINCT distros.name, repos.branch, repos.architecture FROM distros, repos WHERE distros.id = repos.distro_id;")
    for name, branch, arch in cur:
      if name not in self.distros:
        self.distros[name] = {}
      if branch not in self.distros[name]:
        self.distros[name][branch] = []
      if arch not in self.distros[name][branch]:
        self.distros[name][branch].append(arch)
    
    for d in self.distros.keys():
      self.distro.append_text(d)
  
  def add_distro(self, button):
    d = self.distro.get_active_text()
    c = self.color.get_color()
    ages = self.get_combined_age(d,self.packages)
    if len(ages)>0:
      self.distro_store.append([d,c])
      self.graph.add(" ".join([d]+self.packages),ages,c.to_string())
    else:
      print "none"
  
  def add_pkg(self, button):
    p = self.pkg.get_text()
    self.packages.append(p)
    self.pkg_store.append([p])

  def run(self):
    gtk.main()
  
  def get_combined_age(self, distro, packages):
    combined = None
    now = datetime.datetime.now()
    for pkg in packages:
      points = self.get_age(distro, pkg, now)
      point = map(lambda x: (x[0], x[1]//len(packages)),points)
      if combined==None:
        combined = points
      else:
        combined = self.sum_ages(combined, points)
    return combined
  
  def sum_ages(self, aA, aB):
    a = 0
    b = 0
    last_aA = None
    last_aB = None
    result = []
    while a+b<len(aA)+len(aB)-2:
      # the next is in list A
      if a<len(aA)-1 and (len(aB)-1==b or aA[a][0]<aB[b][0]):
        # special case for start
        if a==0 and last_aB==None:
          a+=1
        elif a==0 and last_aB!=None:
          result.append((aA[0][0], aA[0][1]+last_aB[1]))
          a+=1
        elif last_aB!=None:
          result.append((aA[a][0], aA[a][1]+last_aB[1]))
          result.append((aA[a+1][0], aA[a+1][1]+last_aB[1]))
          a+=2
        else:
          a+=1
        last_aA = aA[a-1]
      #equal time start
      elif a==0 and b==0 and aA[a][0]==aB[b][0]:
        result.append((aA[a][0], aA[a][1]+aB[b][1]))
        last_aA = aA[a]
        last_aB = aB[b]
        a+=1
        b+=1
      # equal time non-start
      elif a>0 and b>0 and a<len(aA)-1 and b<len(aB)-1 and aA[a][0]==aB[b][0]:
        result.append((aA[a][0], aA[a][1]+aB[b][1]))
        result.append((aA[a][0], aA[a+1][1]+aB[b+1][1]))
        last_aA = aA[a+1]
        last_aB = aB[b+1]
        a+=2
        b+=2
      elif b<len(aB)-1 and (len(aA)-1==a or aA[a][0]>aB[b][0]):
        # special case for start
        if b==0 and last_aA==None:
          b+=1
        elif b==0 and last_aA!=None:
          result.append((aB[0][0], aB[0][1]+last_aA[1]))
          b+=1
        elif last_aA!=None:
          result.append((aB[b][0], aB[b][1]+last_aA[1]))
          result.append((aB[b+1][0], aB[b+1][1]+last_aA[1]))
          b+=2
        else:
          b+=1
        last_aB = aB[b-1]
      else:
        print "unseen case",a,b
        print aA[a]
        print aB[b]
        break
    result.append((aA[-1][0],aA[-1][1]+aB[-1][1]))
    print "combined"
    for a in result:
      print a
    print
    return result
      
  def get_age(self, distro, package, now=None):
    cur = self.con.cursor()
    #print "query upstream"
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages WHERE releases.package_id = packages.id AND packages.name=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,))

    upstream = []
    for row in cur:
      #print row
      upstream.append(row)

    #print
    #print "query downstream"
    q = "SELECT releases.version, MIN(releases.released) FROM releases, packages, repos, distros WHERE releases.package_id = packages.id AND packages.name=%s AND releases.repo_id=repos.id AND repos.distro_id=distros.id AND distros.name=%s GROUP BY releases.version ORDER BY MIN(releases.released)"
    cur.execute(q,(package,distro))

    downstream = []
    for row in cur:
      #print row
      downstream.append(row)

    upstreams = {}
    latest = []
    ages = []
    last_downstream = None
    ds = False
    u = 0
    d = 0
    #print
    #print "interleave"
    #interleave the dates
    while u+d < len(upstream)+len(downstream):
      is_u = False
      version = None
      date = None
      append = False
      if u<len(upstream) and (len(downstream)==d or upstream[u][1]<=downstream[d][1]):
        #print "upstream",upstream[u]
        version, date = upstream[u]
        upstreams[version] = date
        is_u = True
        append = len(downstream)==d or upstream[u][1]!=downstream[d][1]
        u+=1
      else:
        #print "downstream",downstream[d]
        version, date = downstream[d]
        last_downstream = version
        append = True
        d+=1
      if ds and append:
        if len(latest)==0:
          ages.append((date, date-date))
        else:
          ages.append((date, date-upstreams[latest[0]]))
      #print latest
      if is_u:
        latest.append(version)
        #print latest
      else:
        while len(latest)>0 and latest[0]<=version and latest.pop(0)!=version:
          pass
        #print latest
      if last_downstream!=None and append:
        ds=True
        if len(latest)==0:
          ages.append((date, date-date))
        else:
          ages.append((date, date-upstreams[latest[0]]))
    #print
    #print "age"
    if now==None:
      now = datetime.datetime.now()
    if last_downstream!=None:
      if len(latest)==0:
        ages.append((now, now-now))
      else:
        ages.append((now,now-upstreams[latest[0]]))
    
    print "age of",package
    for a in ages:
      print a
    print
    return ages

av = AgeView()
av.run()
