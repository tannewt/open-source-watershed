TESTS = [(None,"basic"),
         ("xine-ui-0.9.18.tar.gz",["xine-ui",0,"0.9.18",None,None]),
         ("gxine-0.5.1.tar.bz2",["gxine",0,"0.5.1",None,None]),
         ("xine-lib-1.0.3a.tar.gz",["xine-lib",0,"1.0.3a",None,None]),
         (None,"tricky version"),
         ("xine-lib-1-rc4.tar.gz",["xine-lib",0,"1-rc4",None,None]),
         ("xine-lib-1-beta1.tar.gz",["xine-lib",0,"1-beta1",None,None]),
         (None,"mixed filename"),
         ("webmin-1.080-minimal.tar.gz",["webmin-minimal",0,"1.080",None,None]),
         (None,"end src"),
         ("xmovie-1.9.8-src.tar.bz2",["xmovie",0,"1.9.8",None,None])]

def has_alpha(s):
  for c in s:
    if c.isalpha():
      return True
  return False

def has_num(s):
  for c in s:
    if c.isdigit():
      return True
  return False

def parse_filename(fn):
  if fn.endswith(".tar.gz"):
    trimmed = fn[:-7]
  elif fn.endswith(".tar.bz2"):
    trimmed = fn[:-8]
  else:
    return None
  
  if "-" not in trimmed:
      return None
  pkg = []
  ver = []
  past_ver = False
  for bit in trimmed.split("-"):
    if not has_alpha(bit):
      past_ver = True
      ver.append(bit)
    elif past_ver and has_num(bit):
      ver.append(bit)
    elif bit!="src":
      pkg.append(bit)
  
  if len(ver)==0:
    ver.append(pkg.pop())
  
  pkg = "-".join(pkg)
  ver = "-".join(ver)
  
  rel = [pkg,0,ver,None,None]
  print fn,"=>",rel[:3]
  return rel

def test(fn,expected):
  result = parse_filename(fn)
  passed = expected==result
  print "\t"+fn,"=>",result,":",passed
  return passed

if __name__=="__main__":
  print "running tests"
  overall = True
  for fn,expected in TESTS:
    if fn == None:
      print
      print "\t"+expected
      continue
    r = test(fn,expected)
    overall = overall and r
  print
  if overall:
    print "passed all"
  else:
    print "FAILED some"
