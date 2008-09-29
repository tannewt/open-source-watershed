import helper
import debian
import slackware
import ubuntu
import datetime

for url in ["http://" + debian.MIRROR + "/" + debian.START_DIR + "README", "http://" + slackware.MIRROR + "/slackware/README.TXT", "http://" + ubuntu.MIRROR + "/" + ubuntu.HTTP_START_DIR + "hardy/Release"]:
  print "trying", url
  mod = helper.open_url(url,'test_file.tmp')
  print mod, helper.open_url(url,'test_file.tmp', datetime.datetime.fromtimestamp(mod))
