import BaseHTTPServer as server

class WatershedRequestHandler (server.BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path=="/":
      self.crawl_summary()
  
  def crawl_summary(self):
    page = ["<html><body>"]
    body = []
    body.append("Welcome to Watershed.")
    body.append(self.path)
    page.append("<br>".join(body))
    page.append("</body></html>")
    self.wfile.write("".join(page))
    

httpd = server.HTTPServer(('',8000), WatershedRequestHandler)
httpd.serve_forever()
