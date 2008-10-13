import helper
import distros.debian as debian
import distros.slackware as slackware
import distros.ubuntu as ubuntu
import datetime

for url in ["http://" + debian.MIRROR + "/" + debian.START_DIR + "README", "http://" + slackware.MIRROR + "/slackware/README.TXT", "http://" + ubuntu.MIRROR + "/" + ubuntu.HTTP_START_DIR + "hardy-proposed/main/binary-i386/Packages.bz2"]:
  print "trying", url
  mod = helper.open_url(url,'test_file.tmp')
  print mod, helper.open_url(url,'test_file.tmp', mod-datetime.timedelta(weeks=1))
