import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper

HOST, USER, PASSWORD, DB = helper.mysql_settings()

import age

import gtk,gobject
from utils import chart

#age.VERBOSE_RESULT=True

DISTRO_COLORS = {"gentoo":   gtk.gdk.Color( 70*256,  53*256, 124*256),
                 "sabayon":  gtk.gdk.Color(  1*256, 112*256, 202*256),
                 "debian":   gtk.gdk.Color(199*256,   0*256,  54*256),
                 "ubuntu":   gtk.gdk.Color(247*256, 128*256,  38*256),
                 "slackware":gtk.gdk.Color( 80*256, 104*256, 178*256),
                 "fedora":   gtk.gdk.Color(  7*256,  42*256,  96*256),
                 "opensuse": gtk.gdk.Color( 36*256, 168*256,   1*256),
                 "arch":     gtk.gdk.Color( 23*256, 147*256, 209*256)}

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
    self.pkg_store = gtk.ListStore(gobject.TYPE_STRING)
    self.packages = []
    p_tv = gtk.TreeView(self.pkg_store)
    p_tv.set_rules_hint(True)
    p_tv.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    #p_tv.set_headers_visible(False)
    renderer = gtk.CellRendererText()
    p_tv.append_column(gtk.TreeViewColumn("Packages",renderer,text=0))
    p_tv.show()
    vbox2.pack_start(p_tv)
    
    # add package stuff
    h = gtk.HBox()
    self.pkg = gtk.Entry()
    self.pkg.connect("activate",self.add_pkg_cb)
    h.pack_start(self.pkg,False,False)
    self.add = gtk.Button(stock=gtk.STOCK_ADD)
    self.add.connect("clicked",self.add_pkg_cb)
    h.pack_start(self.add,False,False)
    h.show_all()
    vbox2.pack_start(h,False,False)
    
    hbox2 = gtk.HBox()
    hbox2.show()
    hbox2.pack_start(vbox2,False,False)
    
    self.distro_store = gtk.ListStore(gobject.TYPE_STRING,gtk.gdk.Color)
    s = gtk.ScrolledWindow()
    s.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    s.show()
    p_tv.set_vadjustment(s.props.vadjustment)
    l = gtk.TreeView(self.distro_store)
    l.set_rules_hint(True)
    l.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    #l.set_headers_visible(False)
    renderer = gtk.CellRendererText()
    l.append_column(gtk.TreeViewColumn("Distros",renderer,text=0,foreground_gdk=1))
    l.show()
    s.add(l)
    hbox2.pack_start(s)
    vbox.pack_start(hbox2)
    
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
    
    for p in pkgs:
      self.add_pkg(p)
  
  def add_distro(self, button):
    d = self.distro.get_active_text()
    b = self.branch.get_active_text()
    a = self.arch.get_active_text()
    c = self.color.get_color()
    ages = age.get_combined_age(d,self.packages,b,a)
    if len(ages)>0:
      self.distro_store.append([" ".join(map(str,(d,b,a))),c])
      self.graph.add(" ".join(map(str,[d,b,a])+self.packages),ages,c.to_string())
    else:
      print "none"
  
  def add_pkg_cb(self, widget):
    p = self.pkg.get_text()
    self.add_pkg(p)
    self.pkg.set_text("")
  
  def add_pkg(self, pkg):
    self.packages.append(pkg)
    self.pkg_store.append([pkg])
  
  def distro_changed(self, widget):
    distro = self.distro.get_active_text()
    self.color.set_color(DISTRO_COLORS[distro])
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
    print "view",date

  def run(self):
    gtk.main()

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
