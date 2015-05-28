# -*- coding: utf-8 -*-
import urllib2
import ftplib
import datetime
import time
import re
import os

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

    def https_response(self, req, res):
      try:
	res.status += 0
      except:
        res.status = None
      return res

def ftp_open_url(url, filename, last_crawl=None):
	tokens = url.split("/")
	host = tokens[2]
	fn = tokens[-1]
	d = "/".join(tokens[3:-1])
	ftp = None
	for i in range(3):
		try:
			ftp = ftplib.FTP(host,"anonymous",timeout=90)
		except EOFError:
			time.sleep(10)
	if ftp==None:
		return None
	try:
		ftp.cwd(d)
		date = ftp.sendcmd(" ".join(("MDTM",fn))).split()[1]
	except ftplib.error_perm:
		print "WARNING ftp MDTM fail: ", url
		return None
	finally:
		ftp.close()
	
	date = datetime.datetime.strptime(date,"%Y%m%d%H%M%S")
	if last_crawl==None or last_crawl<date:
		request = urllib2.Request(url)
		opener = urllib2.build_opener()
		try:
			datastream = opener.open(request)
		except urllib2.URLError:
			print "urllib2.URLError",url
			return None
		out = open(filename, "w")
		out.write(datastream.read())
		out.close()
		return date
	return None

def http_open_url(url, filename, last_crawl=None):
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
    print datastream.status, url
    return None
  elif datastream.status:
    print datastream.status,#last_crawl
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

def open_url(url, filename, last_crawl=None):
	if url.startswith("http://"):
		return http_open_url(url, filename, last_crawl)
	elif url.startswith("ftp://"):
		return ftp_open_url(url, filename, last_crawl)
	else:
		print "unknown protocol:", url

def http_open_dir(url):
  patterns = ['(<tr><td valign=\"top\">)?(<(a|A)[^>]*>)?(<(img|IMG) [^>]*(ALT|alt)="(?P<dir>[^"]*)"[^>]*>)?(</(A|a)>)?( |</td><td>)?<(A|a)[^>]*>(?P<name>[^<]*)</(A|a)> *(</td><td align=\"right\">)?(?P<modified>[^<>]* [0-9][0-9]:[0-9][0-9])',
              '<tr><td class="n"><a href="[^"]*">(?P<name>[^<]*)</a>.*</td><td class="m">(?P<modified>.* [0-9][0-9]:[0-9][0-9](:[0-9][0-9])?)</td><td class="s">.*</td><td class="t">(?P<dir>.*)</td></tr>',
	      '<tr><td valign="top">&nbsp;</td><td><a[^>]*>(?P<name>[^<]*)</a></td><td align="right">(?P<modified>.* [0-9][0-9]:[0-9][0-9])',
	      '<tr class=\"[eo]\"><td><a[^>]*>(?P<name>[^<]*)</a></td><td>[^<]*</td><td>(-|(?P<modified>[^<]* [0-9][0-9]:[0-9][0-9]))</td></tr>',
	      '<NextMarker>(?P<marker>[^<]+)</NextMarker>',
	      '<Key>(?P<name>[^<]*)</Key>.*?<LastModified>(?P<modified>[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-6][0-9]:[0-6][0-9])\.[0-9]*Z</LastModified>']
  patterns = [re.compile(x) for x in patterns]
  original_url = url
  files = []
  while url:
    filename = "".join(("files/helper/", str(time.time()), "-", url.rsplit("/",1)[1]))
    if open_url(url, filename)==None:
      return None
    url = None
  
    f = open(filename)
    s = f.read()
    for p in patterns:
      num_matches = 0
      for match in p.finditer(s):
        d = match.groupdict()
	if "marker" in d:
	  url = original_url + "?marker=" + d["marker"]
	  continue
        is_dir = ("dir" in d and (d["dir"]=="[DIR]" or d["dir"] == "Directory" or (d["dir"]==None and d["name"][-1]=="/"))) or d["name"][-1]=="/"
	# 2012-06-08T13:35:39.149Z
        date_formats = ["%d-%b-%Y %H:%M", "%Y-%m-%d %H:%M", "%Y-%b-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
        release_time = None
        for date_format in date_formats:
          try:
            release_time = datetime.datetime.strptime(d["modified"], date_format)
	    break
          except:
            pass
        if release_time:
          files.append((is_dir,d["name"],release_time))
        else:
          print "unsupported date format:", d["modified"]
        num_matches += 1
      if num_matches > 0:
        #print "matched pattern:", p.pattern
        break
      else:
        #print "missed pattern:", p.pattern
	pass
    f.close()
  return files

def ftp_open_dir(url):
  x, y, host, d = url.split("/",3)
  ftp = ftplib.FTP(host,"anonymous",timeout=90)
  files = []
  def process_line(line):
    line = line.split()
    is_dir = line[0][0]=="d"
    if ":" in line[-2]:
      time = line[-2]
      year = datetime.datetime.now().year
    else:
      time = "00:00"
      year = line[-2]
    date = datetime.datetime.strptime(" ".join(map(str,(line[-4],line[-3],year,time))),"%b %d %Y %H:%M")
    files.append((is_dir,line[-1],date))
  
  ftp.cwd(d)
  for fn in ftp.nlst():
    fn_only = fn.split("/")[-1]
    try:
      date = ftp.sendcmd(" ".join(("MDTM",fn))).split()[1]
      files.append((False,fn_only,datetime.datetime.strptime(date,"%Y%m%d%H%M%S")))
    except ftplib.error_perm:
      files.append((True,fn_only,None))
  ftp.close()
  return files

def open_dir(url):
  try:
    if url.startswith("ftp://"):
      return ftp_open_dir(url)
    else:
      return http_open_dir(url)
  except urllib2.URLError:
    print "bad http",url
  except Exception, e:
    print "exception", e
  return []

def find_match(s, res):
  i = 1
  for r in res:
    m = r.match(s)
    if m:
      return (i,m)
    i += 1
  return (None, None)

def mysql_settings(comp="local"):
  if "WATERSHED_SERVER" in os.environ:
    comp = os.environ["WATERSHED_SERVER"]
  
  if comp=="local":
    f = open("mysql_settings.txt")
  else:
    f = open("mysql_settings_"+comp+".txt")
  settings = map(lambda x: x.strip(),f.readlines())
  f.close()
  return settings
