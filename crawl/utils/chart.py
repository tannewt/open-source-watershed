from goocanvas import *
import gtk
import datetime

class Axis (Group):
  _start = None
  _end = None
  _orientation = None
  _length = 100
  _type = None
  
  VERTICAL = -1
  HORIZONTAL = 1
  
  def __init__(self,orientation):
    Group.__init__(self)
    self._orientation=orientation
    self.p = polyline_new_line(self,0,0,0,0)
  
  def set_range(self, start, end):
    if type(start)!=type(end):
      print "error: start and end different types"
      print start,type(start)
      print end,type(end)
    else:
      self._type = type(start)
      self._start = start
      self._end = end
      self._redraw()
  
  def set_size(self, length):
    self._length = length
    self._redraw()
  
  def _redraw(self):
    if self._orientation==self.HORIZONTAL:
      points= Points([(0,0), (self._length,0)])
    else:
      points = Points([(0,0), (0,-1*self._length)])
    self.p.props.points = points
  
  def coord(self, value):
    if self._start==None or self._end==None:
      print "error: no start or end values"
    elif self._type!=type(value):
      print value,"(",type(value),"is not of type",self._type
    elif type(value)==datetime.datetime or type(value)==datetime.timedelta:
      return self._orientation*self.time_div((value-self._start),(self._end-self._start))*self._length
    else:
      return self._orientation*(value-self._start)/float(self._end-self._start)*self._length
    return -1
  
  def time_div(self,top,bottom):
    t = self.td_to_microsec(top)
    b = self.td_to_microsec(bottom)
    if b==0:
      return 0
    return float(t)/b
    
  def td_to_microsec(self,t):
    return t.microseconds+1000000*t.seconds+1000000*3600*24*t.days
    
    
class LineChart(Canvas):
  lines = {}
  
  def __init__(self):
    Canvas.__init__(self)
    self.connect("size-allocate",self._resize)
    #self.connect("motion-notify-event",self.mousemove)
    self.props.anchor = gtk.ANCHOR_SW
    self._y_axis = Axis(Axis.VERTICAL)
    left,top,right,bottom = self.get_bounds()
    self._y_axis.translate(50,bottom-50)
    self._x_axis = Axis(Axis.HORIZONTAL)
    left,top,right,bottom = self.get_bounds()
    self._x_axis.translate(50,bottom-50)
    self.root = self.get_root_item()
    self.root.add_child(self._y_axis)
    self.root.add_child(self._x_axis)
  
  def add(self,title, data, color="#ffffffffffff"):
    line = polyline_new_line(self.root,0,0,0,0)
    line.props.stroke_color = color
    line.translate(50,self.get_bounds()[3]-50)
    xs = map(lambda x: x[0], data)
    ys = map(lambda y: y[1], data)
    if self._x_axis._start==None or self._y_axis._start==None:
      self._x_axis.set_range(min(xs), max(xs))
      self._y_axis.set_range(min(ys), max(ys))
    else:
      self._x_axis.set_range(min(xs + [self._x_axis._start]), max(xs + [self._x_axis._end]))
      self._y_axis.set_range(min(ys + [self._y_axis._start]), max(ys + [self._y_axis._end]))
    self._adjust_points(line,data)
    self.lines[title] = [line,data]
  
  def _adjust_points(self, line, data):
    line.props.points = Points(map(lambda d: (self._x_axis.coord(d[0]),self._y_axis.coord(d[1])),data))
  
  def remove(self,title):
    pass
  
  def hide(self,title):
    pass
  
  def _resize(self, widget, allocation):
    w,h = allocation.width,allocation.height
    self.set_bounds(0,0,w,h)
    self._y_axis.set_simple_transform(50,h-50,1,0)
    self._y_axis.set_size(h-75)
    self._x_axis.set_simple_transform(50,h-50,1,0)
    self._x_axis.set_size(w-75)
    
    map(lambda k: self.lines[k][0].set_simple_transform(50,h-50,1,0),self.lines.keys())
    map(lambda l: self._adjust_points(self.lines[l][0],self.lines[l][1]),self.lines.keys())
  
  def mousemove(self, target, event):
    print event.get_coords()
