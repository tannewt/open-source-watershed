from .utils import helper
import re
import time

NAME = "subversion"

def find_match(s, res):
  i = 1
  for r in res:
    m = r.match(s)
    if m:
      return (i,m)
    i += 1
  return (None, None)

def get_date(m_d):
  if m_d.has_key("day") and m_d["day"]:
    if m_d.has_key("smonth") and m_d["smonth"]:
      try:
        return time.strptime(" ".join([m_d["day"],m_d["smonth"],m_d["year"]]),"%d %b %Y")
      except e:
        print "ERROR: parsing date failed: %s"%e
    elif m_d.has_key("month"):
      #special case
      if m_d["month"]=="Sept":
        m_d["month"]="September"
      try:
        return time.strptime(" ".join([m_d["day"],m_d["month"],m_d["year"]]),"%d %B %Y")
      except e:
        print "ERROR: parsing date failed: %s"%e
    else:
      return None
  return None

def get_releases(last_crawl=None):
  pkgs = []
  filename = "files/subversion/CHANGES-" + str(time.time())
  info = helper.open_url("http://svn.collab.net/repos/svn/trunk/CHANGES",filename,last_crawl)
  if info==None:
    return pkgs
  
  changes = open(filename)
  date = "(?P<day>[0-9][0-9]?) ((?P<smonth>[A-Z][a-z][a-z])|(?P<month>[A-Z][a-z]+)) (?P<year>[0-9]{4})"
  version = "(?P<version>[0-9\.]+)"
  bracket_stuff = "( \[.*\])?"
  #                   Version 1.1.3
  form1 = re.compile("^Version "+version+bracket_stuff+"$")
  
  # (5 July 2005, from /branches/1.2.x)
  form1_line2_2 = re.compile("^\([a-z]* ?"+date)
  # (?? ??? 2008, from /branches/1.5.x)
  form1_line2_3 = re.compile("^\(\?\? \?\?\? [0-9]+")


  
  #Version 0.35.1 [Beta] (branching 19 December 2003, from /tags/0.35.0)
  #Version 0.35.0 (branching 12 December 2003, from revision 7994)
  form2 = re.compile("^Version "+version+bracket_stuff+" \([a-z]+ "+date)
  
  #Milestones M4/M5  (released 19 Oct 2001, revision 271)
  #Milestone M3  (released 30 Aug 2001, revision 1)
  form3 = re.compile("^Milestone(s)? (?P<version>M[0-9](/M[0-9])?)  \([a-z]+ "+date)

  first_line = [form1, form2, form3]
  second_line = [form1_line2_2, form1_line2_3]
  versions = 0

  empty = 2
  rel = [None, None, None]
  pkg = []
  second = False
  for line in changes:
    line = line.strip("\n")
    if line == "":
      empty+=1
      continue
    
    if empty>=2:
      form,m = find_match(line, first_line)
      if m:
        versions += 1
        if rel[0] and rel[1]:
          rel[-1] = "".join(pkg)
          pkgs.append(rel)
        else:
          print "skipped",rel[0]
        rel = [None, None, None]
        pkg = [line]
        empty = 0
        m_d = m.groupdict()
        if m_d.has_key("version"):
          rel[0] = m_d["version"]
        
        rel[1] = get_date(m_d)
        second = True
    else:
      pkg.append(line)
      if rel[1]==None and second:
        second = False
        form,m = find_match(line, second_line)
        if m:
          m_d = m.groupdict()
          rel[1] = get_date(m_d)
  print versions,"=",len(pkgs)
  return pkgs
