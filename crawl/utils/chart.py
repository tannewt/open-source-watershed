from goocanvas import *
import gtk
import datetime

class Axis (Group):
  VERTICAL = -1
  HORIZONTAL = 1
  
  def __init__(self,orientation):
    Group.__init__(self)
    self._orientation=orientation
    self.p = polyline_new_line(self,0,0,0,0)
    self._start = None
    self._end = None
    self._length = 100
    self._type = None
    self._grid = []
  
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
  
  def _draw_grid(self):
    for i in range(len(self._grid)):
      item = self._grid.pop()
      p = item.get_parent()
      #print item, p, self
      index = p.find_child(item)
      p.remove_child(index)
    
    if type(self._start)==datetime.datetime:
      # draw lines per year
      year = datetime.datetime(self._start.year+1,1,1)
      while year<self._end:
        #print "draw year",year
        line = polyline_new_line(self,0,0,0,0)
        c = self.coord(year)
        text = Text(text=str(year.year))
        self.add_child(text,-1)
        if self._orientation==self.HORIZONTAL:
          points= Points([(c,-5), (c,5)])
          text.props.anchor = gtk.ANCHOR_NORTH
          text.props.x = c
          text.props.y = 6
        else:
          points = Points([(-5,c), (5,c)])
          text.props.anchor = gtk.ANCHOR_EAST
          text.props.x = -6
          text.props.y = c
        line.props.points = points
        self._grid.append(line)
        self._grid.append(text)
        year = year.replace(year=year.year+1)
        
      if self._start.month==12:
        month = datetime.datetime(self._start.year,1,1)
      else:
        month = datetime.datetime(self._start.year,self._start.month+1,1)
      while month<self._end:
        #print "draw year",year
        if month.month==1:
          if month.month==12:
            month = month.replace(year=month.year+1,month=1)
          else:
            month = month.replace(month=month.month+1)
          continue
          
        line = polyline_new_line(self,0,0,0,0)
        c = self.coord(month)
        text = Text(text=str(month.month))
        self.add_child(text,-1)
        if self._orientation==self.HORIZONTAL:
          points= Points([(c,-3), (c,3)])
          text.props.anchor = gtk.ANCHOR_NORTH
          text.props.x = c
          text.props.y = 4
        else:
          points = Points([(-3,c), (3,c)])
          text.props.anchor = gtk.ANCHOR_EAST
          text.props.x = -4
          text.props.y = c
        line.props.points = points
        self._grid.append(line)
        self._grid.append(text)
        if month.month==12:
          month = month.replace(year=month.year+1,month=1)
        else:
          month = month.replace(month=month.month+1)
    elif type(self._start)==datetime.timedelta:
      spread = self._end - self._start
      if spread<datetime.timedelta(weeks=4):
        one_day = datetime.timedelta(days=1)
        # draw lines per day
        day = datetime.timedelta(days=self._start.days+1)
        while day<self._end:
          #print "draw day",day
          line = polyline_new_line(self,0,0,0,0)
          c = self.coord(day)
          if self._orientation==self.HORIZONTAL:
            points= Points([(c,-2), (c,2)])
          else:
            points = Points([(-2,c), (2,c)])
          line.props.points = points
          self._grid.append(line)
          day += one_day
      
      # draw lines per week
      if spread<datetime.timedelta(weeks=60):
        one_week = datetime.timedelta(weeks=1)
        # draw lines per day
        week = datetime.timedelta(weeks=(self._start.days/7)+1)
        while week<self._end:
          #print "draw week",week
          line = polyline_new_line(self,0,0,0,0)
          c = self.coord(week)
          if self._orientation==self.HORIZONTAL:
            points= Points([(c,-3), (c,3)])
            
          else:
            points = Points([(-3,c), (3,c)])
            
          line.props.points = points
          self._grid.append(line)
          week += one_week
      one_month = datetime.timedelta(weeks=4)
      # draw lines per day
      month = datetime.timedelta(weeks=(self._start.days/(7*4))+1)
      i = 0
      while month<self._end:
        #print "draw month",month
        line = polyline_new_line(self,0,0,0,0)
        c = self.coord(month)
        
        text = Text(text=str(i))
        self.add_child(text,-1)
        if self._orientation==self.HORIZONTAL:
          points= Points([(c,5), (c,-5)])
          text.props.anchor = gtk.ANCHOR_NORTH
          text.props.x = c
          text.props.y = 6
        else:
          points = Points([(-5,c), (5,c)])
          text.props.anchor = gtk.ANCHOR_EAST
          text.props.x = -6
          text.props.y = c
        line.props.points = points
        self._grid.append(line)
        self._grid.append(text)
        i += 1
        month += one_month
    else:
      pass
  
  def _redraw(self):
    self._draw_grid()
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
    
    self._move_points()
    
    self._adjust_points(line,data)
    notes = self._draw_notes(title,data,color)
    self.lines[title] = [line,data,notes,color]
  
  def _adjust_points(self, line, data):
    line.props.points = Points(map(lambda d: (self._x_axis.coord(d[0]),self._y_axis.coord(d[1])),data))
  
  def _adjust_notes(self, notes, data,w,h):
    i = 0
    for i in range(len(notes)):
      notes[i][0].props.center_x = self._x_axis.coord(data[notes[i][1]][0])
      notes[i][0].props.center_y = self._y_axis.coord(data[notes[i][1]][1])
      if w!=None and h!=None:
        notes[i][0].set_simple_transform(50,h-50,1,0)
    
  def _draw_notes(self,line,data,color="#ffffffffffff"):
    radius = 3
    circles = []
    i = 0
    for point in data:
      if point[2]!=None:
        circle = Ellipse(parent=self.root,center_x=self._x_axis.coord(point[0]),center_y = self._y_axis.coord(point[1]),radius_x = radius,radius_y = radius,stroke_color = color,fill_color="#ffffffffffff",title="test")
        circle.translate(50,self.get_bounds()[3]-50)
        circle.connect("enter_notify_event",self.on_enter_notify,line,i)
        circle.connect("leave_notify_event",self.on_leave_notify,line,i)
        circle.connect("button_press_event", self.on_button_press,line,i)
        circle.connect("button_release_event", self.on_button_release,line,i)
        circles.append((circle,i))
        #print circle
      i += 1
    return circles
  
  def on_enter_notify(self, item, target, event, line, index):
    #print "enter",line[:12],index
    item.props.fill_color = self.lines[line][3]
  
  def on_leave_notify(self, item, target, event, line, index):
    #print "leave",line[:12],index
    item.props.fill_color = "#ffffffffffff"
  
  def on_button_press(self, item, target, event, line, index):
    #print "press",line[:12],index
    print self.lines[line][1][index][2]
  
  def on_button_release(self, item, target, event, line, index):
    #print "release",line[:12],index
    pass
  
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
    self._move_points(w,h)
  
  def _move_points(self,w=None,h=None):
    map(lambda l: self._adjust_points(self.lines[l][0],self.lines[l][1]),self.lines.keys())
    map(lambda l: self._adjust_notes(self.lines[l][2],self.lines[l][1],w,h),self.lines.keys())
  
  def mousemove(self, target, event):
    print event.get_coords()
