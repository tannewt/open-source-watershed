import datetime

class VersionNode:
  def __init__(self,date=None):
    self.tokens = []
    self.children = {}
    self.date = date
  
  def add(self, date, tokens):
    if len(tokens) == 0:
      self.date = date
    else:
      if tokens[0] not in self.tokens:
        self.tokens.append(tokens[0])
        self.children[tokens[0]] = VersionNode()
      self.children[tokens[0]].add(date, tokens[1:])
  
  def next(self, tokens):
    """Given a series of tokens return its release date and all subtrees with later versions."""
    if len(tokens)==0:
      return (self.date,[])
    else:
      if tokens[0] in self.tokens:
        date,children = self.children[tokens[0]].next(tokens[1:])
        return (date,children + map(lambda x: self.children[x], self.tokens[self.tokens.index(tokens[0])+1:]))
      else:
        return None
  
  def after(self, date):
    c = map(lambda k: self.children[k].after(date),self.children)
    if len(c)>0:
      c = min(c)
    else:
      c = datetime.datetime(9999,12,31)
    
    if self.date!=None and self.date > date:
      return min(self.date, c)
    else:
      return c
  
  def __str__(self, prefix="", indent=0):
    result = ["  "*indent + str(self.date)]
    for t in self.tokens:
      v = prefix + str(t)
      result.append("  "*indent + v)
      result.append(self.children[t].__str__(v, indent+1))
    return "\n".join(result)

class VersionTree:
  def __init__(self):
    self.root = VersionNode()
  
  def add_release(self, date, version):
    self.root.add(date, self._tokenize(version))
  
  def compute_lag(self, date, version):
    print self.root
    d,newer = self.root.next(self._tokenize(version))
    oldest_new = min(map(lambda r: r.after(d),newer))
    print oldest_new
    if oldest_new != datetime.datetime(9999,12,31):
      return date - oldest_new
    else:
      return date - date
  
  def _tokenize(self, v):
    tokens = []
    token = v[0]
    num = v[0].isdigit()
    for c in v[1:]:
      if num and not c.isdigit():
        tokens.append(int(token))
        token = c
        num = False
      elif not num and c.isdigit():
        tokens.append(token)
        token = c
        num = True
      else:
        token += c
    if num:
      tokens.append(int(token))
    else:
      tokens.append(token)
    
    return tokens
  
  def __str__(self):
    return str(self.root)

if __name__=="__main__":
  t = VersionTree()
  print t._tokenize("2.6.28.10")
  
  t.add_release(datetime.datetime(2009, 3, 1), "2.0")
  t.add_release(datetime.datetime(2009, 3, 2), "2.1")
  t.add_release(datetime.datetime(2009, 3, 3), "3.0")
  t.add_release(datetime.datetime(2009, 3, 4), "2.2")
  print t
  
  print t.compute_lag(datetime.datetime(2009, 3, 5), "2.1")
