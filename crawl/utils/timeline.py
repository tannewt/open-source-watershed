import UserDict
import bisect
from datetime import datetime, timedelta
def td_to_microsec(t):
    return t.microseconds+1000000*t.seconds+1000000*3600*24*t.days

def td_div(s,o):
  return float(td_to_microsec(s))/td_to_microsec(o)

class Timeline(UserDict.DictMixin):
  """This timeline stores any value for a particular time."""
  def __init__(self, data=[]):
    self._dates = []
    self._values = {}
    
    last_date = None
    for date,value in data:
      if last_date != None and last_date>=date:
        print "error"
        return
      self._dates.append(date)
      self._values[date] = value
  
  def first_date(self):
    if len(self._dates)>0:
      return self._dates[0]
    return None
  
  def last_date(self):
    if len(self._dates)>0:
      return self._dates[-1]
    return None
  
  def __eq__(self, other):
    if None == other:
      return False
    return self._values==other._values
  
  def __ne__(self, other):
    if None == other:
      return True
    return self._values!=other._values
  
  def __getitem__(self, date):
    """Get the value at this date or earlier."""
    if type(date)==slice:
      step = None
      if step==None:
        start = None
        stop = None
        if date.start!=None and type(date.start)==datetime:
          start = bisect.bisect_left(self._dates,date.start)
        else:
          start = date.start
        if date.stop!=None and type(date.start)==datetime:
          stop = bisect.bisect_left(self._dates,date.stop)
        else:
          stop = date.stop
        
        result = []
        for d in self._dates[start:stop]:
          result.append((d,self._values[d]))
        return Timeline(result)
    else:
      if type(date)==datetime:
        i = bisect.bisect_left(self._dates,date)
        index=False
      else:
        i = date
        index = True
      #print date, i, self._dates
      if i == len(self._dates) or (not index and self._dates[i]!=date):
        return None
      d = self._dates[i]
      v = self._values[d]
      if index:
        return (d,v)
      else:
        return v
  
  def __setitem__(self, date, value):
    """Set the value for this date."""
    i = bisect.bisect_left(self._dates,date)
    if i < len(self) and self._dates[i] == date:
      self._values[date] = value
    else:
      self._dates.insert(i,date)
      self._values[date] = value
  
  def __delitem__(self, date):
    """Remove the date."""
    if date in self._dates:
      del self._values[date]
      self._dates.remove(date)
  
  def keys(self):
    return self._dates
  
  def __contains__(self, date):
    """Whether the timeline span contains the date."""
    return self._dates[0] <= date and date <= self._dates[-1]
  
  def __add__(self, other):
    """Union the two timelines together."""
    i = 0
    j = 0
    result = Timeline()
    while i<len(self) and j<len(other):
      date = None
      if self._dates[i] <= other._dates[j]:
        date = self._dates[i]
        result[date] = self[date] 
        i+=1
      else:
        date = other._dates[j]
        result[date] = other[date]
        j+=1
    
    if i!=len(self):
      more = self[i:]
    elif j!=len(other):
      more = other[j:]
    else:
      more = None
    
    if more!=None:
      for date in more:
        result[date] = more[date]
    return result
  
  def __iadd__(self, other):
    """Union the two timelines together."""
    for date in other._dates:
      if date in self._dates:
        self[date] += other[date]
      else:
        self[date] = other[date]
    
    return self
  
  def __sub__(self, other):
    """Remove date-value pairs in other from self."""
    print "sub",self,other
    pass
  
  def __mul__(self, other):
    result = []
    for date in self._dates:
      result.append((date, self[date]*other))
    return Timeline(result)
  
  def __rmul__(self, other):
    return self*other
  
  def __imul__(self, other):
    for date in self._dates:
      self._values[date] *= other
    return self
  
  def __div__(self, other):
    result = []
    for date in self._dates:
      result.append((date, self[date]/other))
    return Timeline(result)
  
  def __idiv__(self, other):
    for date in self._dates:
      self[date] /= other
    return self
  
  
  def __repr__(self):
    points = []
    for d in self._dates:
      points.append("".join(("(",d.__repr__(),",",self._values[d].__repr__(),")")))
    return "".join(("Timeline([",",".join(points),"])"))

class StepTimeline(Timeline):
  def __getitem__(self, date):
    """Get the value at this date or earlier."""
    if type(date)==slice:
      step = None
      if step==None:
        start = None
        stop = None
        if date.start!=None and type(date.start)==datetime:
          start = bisect.bisect_left(self._dates,date.start)
        else:
          start = date.start
        if date.stop!=None and type(date.start)==datetime:
          stop = bisect.bisect_left(self._dates,date.stop)
        else:
          stop = date.stop
        
        result = []
        for d in self._dates[start:stop]:
          result.append((d,self._values[d]))
        return Timeline(result)
    else:
      i = bisect.bisect_left(self._dates,date)
      #print date, i, self._dates[i-1],self._values[self._dates[i-1]]
      if i == 0 and self._dates[i]>date:
        return 0
      if i<len(self._dates) and self._dates[i]==date:
        return self._values[date]
      d = self._dates[i-1]
      return self._values[d]
  
  def merge_dates(self, d1, d2):
    i = 0
    j = 0
    result = []
    while i<len(d1) and j<len(d2):
      if d1[i] <= d2[j]:
        result.append(d1[i])
        i+=1
      else:
        result.append(d2[j])
        j+=1
    if i<len(d1):
      rest = d1[i:]
    elif j<len(d2):
      rest = d2[j:]
    else:
      rest = None
    
    if rest!=None:
      for d in rest:
        result.append(d)
    return result
  
  def __add__(self, other):
    result = Timeline()
    for date in self.merge_dates(self._dates, other._dates):
      result[date] = self[date]+other[date]
    return result
  
  def __mul__(self, other):
    result = Timeline()
    for date in self.merge_dates(self._dates, other._dates):
      result[date] = self[date]*other[date]
    return result
  
  def __div__(self, other):
    result = Timeline()
    for date in self.merge_dates(self._dates, other._dates):
      result[date] = self[date]/other[date]
    return result

class ConnectedTimeline(StepTimeline):
  def __getitem__(self, date):
    """Get the value at this date or earlier."""
    if type(date)==slice:
      step = None
      if step==None:
        start = None
        stop = None
        if date.start!=None and type(date.start)==datetime:
          start = bisect.bisect_left(self._dates,date.start)
        else:
          start = date.start
        if date.stop!=None and type(date.start)==datetime:
          stop = bisect.bisect_left(self._dates,date.stop)
        else:
          stop = date.stop
        
        result = []
        for d in self._dates[start:stop]:
          result.append((d,self._values[d]))
        return Timeline(result)
    else:
      i = bisect.bisect_left(self._dates,date)
      #print date, i, self._dates[i-1],self._values[self._dates[i-1]]
      if i == 0 and self._dates[i]>date:
        return 0
      if i<len(self._dates) and self._dates[i]==date:
        return self._values[date]
      d1 = self._dates[i-1]
      if i==len(self._dates):
        return self._values[d1]
      d2 = self._dates[i]
      return self._values[d1]+(self._values[d2]-self._values[d1])*(td_div((date-d1),(d2-d1)))
  
  def __repr__(self):
    return "Connected"+Timeline.__repr__(self)
