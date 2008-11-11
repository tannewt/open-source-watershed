import gtk
import os
import sys

sys.path.append(os.getcwd())

from utils import chart

window = gtk.Window()
window.set_default_size(500,300)
window.show()

graph = chart.LineChart()
graph.add("line",[(0.0,0.0),(1.0,1.5),(2.0,2.0)])

window.add(graph)
graph.show()


window.connect("destroy",lambda x: gtk.main_quit())

gtk.main()
