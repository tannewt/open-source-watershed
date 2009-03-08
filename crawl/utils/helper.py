import urllib2
import ftplib
import datetime
import time
import re

class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)       
        result.status = code
        return result
    
    def http_response(self, req, res):
      try:
        res.status += 0
      except:
        res.status = None
      return res

def open_url(url, filename, last_crawl=None):
  request = urllib2.Request(url)
  request.add_header('Accept','text/html,application/xhtml+xml,application/xml,q=0.9,*/*;q=0.8')
  request.add_header('Accept-Language','en-us,en;q=0.5')
  request.add_header('Accept-Charset','ISO-8859-1')
  if last_crawl!=None:
    last_crawl = last_crawl.strftime("%a, %d %b %Y %H:%M:%S PST")
    #                                                     Thu, 15 Apr 2004 19:45:21 GMT
    request.add_header('If-Modified-Since', last_crawl)
  opener = urllib2.build_opener(DefaultErrorHandler())
  datastream = opener.open(request)
  
  if datastream.status == 404:
    print datastream.status,#url,
    return None
  elif datastream.status:
    print datastream.status,#last_crawl,
    return None
  else:
    out = open(filename, "w")
    out.write(datastream.read())
    out.close()
    try:
      date = datastream.headers.dict['last-modified']
    except:
      date = datastream.headers.dict['date']
    return datetime.datetime.strptime(date,"%a, %d %b %Y %H:%M:%S %Z")

def open_dir(url):
  filename = "".join(("files/helper/", str(time.time()), "-", url.rsplit("/",1)[1]))
  if open_url(url, filename)==None:
    return None
  
  pattern = '(<tr><td valign=\"top\">)?(<(img|IMG) [^>]*(ALT|alt)="(?P<dir>[^"]*)"[^>]*>)?( |</td><td>)?<(A|a)[^>]*>(?P<name>[^<]*)</(A|a)> *(</td><td align=\"right\">)?(?P<modified>.* [0-9][0-9]:[0-9][0-9]).*'
  pattern = re.compile(pattern)

  f = open(filename)
  files = []
  for line in f:
    match = pattern.match(line)
    if match:
      d = match.groupdict()
      is_dir = d["dir"]=="[DIR]" or (d["dir"]==None and d["name"][-1]=="/")
        
      files.append((is_dir,d["name"],datetime.datetime.strptime(d["modified"],"%d-%b-%Y %H:%M")))
  f.close()
  return files

def find_match(s, res):
  i = 1
  for r in res:
    m = r.match(s)
    if m:
      return (i,m)
    i += 1
  return (None, None)

def mysql_settings():
  f = open("mysql_settings.txt")
  settings = map(lambda x: x.strip(),f.readlines())
  f.close()
  return settings
