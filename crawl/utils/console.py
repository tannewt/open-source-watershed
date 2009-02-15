import sys
# Debian (0/40)                               134
# [==========>----------------------------------]
# experimental experimental contrib s390
class CrawlStatus:
  def __init__(self):
    self.distro = None
    self.total = None
    self.done = None
    self.new = 0
    self.repo = None
    
    self._length = None
  
  def set_status(self, done, new, repo):
    self.repo = repo
    self.done = done
    self.new = new
    self.redraw()
  
  def next(self, distro, total):
    self.repo = "gathering"
    self.done = 0
    self.new = 0
    self.total = total
    self.distro = distro
    self._length = 0
    print
    self.redraw()
  
  def get_text():
    w = "["+"="*50+" "*28+"]"
    return w
  
  def redraw():
    if self._length!=None:
      sys.stdout.write('\x08'*self._length)
    t = get_text()
    self._length = len(t)
    sys.stdout.write(t)
    sys.stdout.flush()
