import urllib2
import datetime

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
  if last_crawl:
    last_crawl = last_crawl.strftime("%a, %d %b %Y %H:%M:%S PST")
    #                                                     Thu, 15 Apr 2004 19:45:21 GMT
    request.add_header('If-Modified-Since', last_crawl)
  opener = urllib2.build_opener(DefaultErrorHandler())
  datastream = opener.open(request)
  
  if datastream.status == 404:
    print datastream.status,#url,
    return None
  elif datastream.status:
    print datastream.status,
    return None
  else:
    out = open(filename, "w")
    out.write(datastream.read())
    out.close()
    return datetime.datetime.strptime(datastream.headers.dict['last-modified'],"%a, %d %b %Y %H:%M:%S %Z")
