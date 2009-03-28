import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

import age

try:
	import gtk
	import gobject
	HEADLESS=False
except:
	print "headless!"
	HEADLESS=True
from utils import chart
from utils.history import *

#age.VERBOSE_RESULT=True

DISTRO_COLORS = {"gentoo":   ( 70*256,  53*256, 124*256),
                 "sabayon":  (  1*256, 112*256, 202*256),
                 "debian":   (199*256,   0*256,  54*256),
                 "ubuntu":   (247*256, 128*256,  38*256),
                 "slackware":( 80*256, 104*256, 178*256),
                 "fedora":   (  7*256,  42*256,  96*256),
                 "opensuse": ( 36*256, 168*256,   1*256),
                 "arch":     ( 23*256, 147*256, 209*256),
                 "funtoo":   ( 178*256, 129*256, 227*256)}

class AgeView:
  def __init__(self, pkgs=[]):
    self.window = gtk.Window()
    self.window.set_default_size(500,300)
    self.window.show()

    hbox = gtk.VPaned()
    hbox.show()
    
    self.graph = chart.LineChart()
    self.graph.set_size_request(500,200)
    self.graph.connect('select',self.select)

    hbox.pack1(self.graph,True)
    self.graph.show()

    vbox = gtk.VBox()
    vbox.show()
    
    # add distro stuff
    h = gtk.HBox()
    self.distro = gtk.combo_box_new_text()
    self.distro.connect("changed",self.distro_changed)
    h.add(self.distro)
    self.branch = gtk.combo_box_new_text()
    self.branch.connect("changed",self.branch_changed)
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
    vbox2 = gtk.VBox()
    vbox2.show()
    self.pkg_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING)
    self.packages = []
    p_tv = gtk.TreeView(self.pkg_store)
    #p_tv.set_fixed_height_mode(True)
    p_tv.set_rules_hint(True)
    p_tv.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    #p_tv.set_headers_visible(False)
    renderer = gtk.CellRendererText()
    p_tv.append_column(gtk.TreeViewColumn("Packages",renderer,markup=0))
    p_tv.append_column(gtk.TreeViewColumn("Version",renderer,text=1))
    p_tv.show()
    sp = gtk.ScrolledWindow()
    sp.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
    sp.show()
    sp.add(p_tv)
    vbox2.pack_start(sp)
    
    hbox2 = gtk.HBox()
    hbox2.show()
    hbox2.pack_start(vbox2,False,False)
    
    self.distro_store = gtk.ListStore(str)
    s = gtk.ScrolledWindow()
    s.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_ALWAYS)
    s.show()
    s.set_vadjustment(sp.props.vadjustment)
    self.distro_view = gtk.TreeView(self.distro_store)
    #self.distro_view.set_fixed_height_mode(True)
    self.distro_view.set_rules_hint(True)
    self.distro.set_size_request(-1,-1)
    self.distro_view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    #l.set_headers_visible(False)
    self.distro_view.show()
    s.add(self.distro_view)
    hbox2.pack_start(s)
    vbox.pack_start(hbox2)
    
    # add package stuff
    h = gtk.HBox()
    self.pkg = gtk.Entry()
    self.pkg.connect("activate",self.add_pkg_cb)
    h.pack_start(self.pkg,False,False)
    self.add = gtk.Button(stock=gtk.STOCK_ADD)
    self.add.connect("clicked",self.add_pkg_cb)
    h.pack_start(self.add,False,False)
    h.show_all()
    vbox.pack_start(h,False,False)
    
    
    
    hbox.add(vbox)
    
    self.window.add(hbox)
    self.window.connect("destroy",lambda x: gtk.main_quit())
    
    HOST, USER, PASSWORD, DB = helper.mysql_settings()

    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    
    self.distros = {}
    cur = con.cursor()
    cur.execute("SELECT DISTINCT distros.name, repos.branch, repos.architecture FROM distros, repos WHERE distros.id = repos.distro_id;")
    for name, branch, arch in cur:
      if name not in self.distros:
        self.distros[name] = {}
      if branch not in self.distros[name]:
        self.distros[name][branch] = []
      if arch not in self.distros[name][branch]:
        self.distros[name][branch].append(arch)
    con.close()
    
    for d in self.distros.keys():
      self.distro.append_text(d)
    
    self.current = datetime.now()
    
    self._histories = []
    for p in pkgs:
      self.add_pkg(p)
  
  def add_distro(self, button):
    d = self.distro.get_active_text()
    b = self.branch.get_active_text()
    a = self.arch.get_active_text()
    c = self.color.get_color()
    distro = DistroHistory(d,self.packages,b,a)
    key = "|".join(map(str,(d,b,a)))
    self._histories.append(distro)
    self.new_distro_store([distro])
    if len(distro.timeline)>0:
      #distro.notes
      self.graph.add(key,distro.timeline,[],c.to_string())
    else:
      print "none"
  
  def add_pkg_cb(self, widget):
    p = self.pkg.get_text()
    self.add_pkg(p)
    self.pkg.set_text("")
  
  def add_pkg(self, pkg):
    try:
      pkg = PackageHistory(pkg)
    except Exception:
      print "unknown package",pkg
      return
    self.packages.append(pkg)
    for distro in self._histories:
      distro.add_pkg(pkg)
      self.graph.update("|".join(map(str,(distro.name,distro.branch,distro.arch))),distro.timeline, distro.notes)
    if not pkg.ish:
      string = "<b>"+pkg.name+"</b>"
    else:
      string = pkg.name
    self.pkg_store.append([string, str(pkg.timeline.last(self.current))])
    if len(self._histories)>0:
      self.distro_store.append((str,)*len(self._histories))
    else:
      self.distro_store.append(("",))
    self.update_downstream()
  
  def distro_changed(self, widget):
    distro = self.distro.get_active_text()
    self.color.set_color(gtk.gdk.Color(*DISTRO_COLORS[distro]))
    self.branch.props.model.clear()
    for d in self.distros[distro].keys():
      self.branch.append_text(d)
  
  def branch_changed(self, widget):
    distro = self.distro.get_active_text()
    branch = self.branch.get_active_text()
    if distro!=None and branch!=None:
      self.arch.props.model.clear()
      for a in self.distros[distro][branch]:
        self.arch.append_text(a)
  
  def select(self, widget, date):
    self.current = date
    self.update_upstream()
    self.update_downstream()
  
  def update_upstream(self):
    i = 0
    for p in self.packages:
      self.pkg_store[i][1] = str(p.timeline.last(self.current))
      i += 1
  
  def update_downstream(self):
    c = 0
    for d in self._histories:
      r = 0
      for version,lag in d.snapshot(self.current):
        if version == None:
          content = ""
        elif lag==timedelta():
          content = "<b>"+version+"</b>"
        elif lag.days>7:
          content = version + " ~ " + str(lag.days/7)+" weeks"
        else:
          content = version + " ~ " + str(lag.days)+" days"
        self.distro_store[r][c] = content
        r += 1
      c += 1
  
  def new_distro_store(self,new=[]):
    self.distro_store = gtk.ListStore(*((str,)*len(self._histories)))
    for i in range(len(self.packages)):
      self.distro_store.append(("",)*len(self._histories))
    self.distro_view.set_model(self.distro_store)
    
    renderer = gtk.CellRendererText()
    
    i = len(self._histories)-len(new)
    for d in new:
      self.distro_view.append_column(gtk.TreeViewColumn(d.name,renderer,markup=i))
      i+=1
    
    self.update_downstream()

  def run(self):
    gtk.main()

if __name__=="__main__":
  if "--verbose" in sys.argv:
    age.VERBOSE_RESULT = True
    sys.argv.remove("--verbose")

  pkgs = []
  if len(sys.argv)>1:
    f = open(sys.argv[1])
    pkgs = map(lambda x: x.strip(), f.readlines())
    pkgs = filter(lambda s: s[0]!="#", pkgs)
    f.close()
  av = AgeView(pkgs)
  av.run()
