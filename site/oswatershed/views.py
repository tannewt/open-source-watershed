# Create your views here.
import os

from django.http import HttpResponse
from django.shortcuts import render_to_response

from utils.history import PackageHistory
from utils.stats import DataStats, PackageStats
from utils.crawlhistory import CrawlHistory

def index(request):
  s = DataStats()
  upstream = CrawlHistory()
  rest = []
  for distro in ["arch","debian", "fedora", "funtoo", "gentoo", "opensuse", "sabayon", "slackware", "ubuntu"]:
    ch = CrawlHistory(None,distro)
    rest.append((distro,ch.today,ch.releases[:5]))
  
  return render_to_response('index.html',
    {"stats": s,
    "crawl_stats":[("Upstream",upstream.today,upstream.releases[:5])]+rest
    }
  )

def distro(request, distro):
  return HttpResponse("Hello, this is the distro page for %s."%(distro,))

STAT_DISTROS = [("arch","current"),("arch","future"),
                ("debian","current"),("debian","future"),
                ("fedora","current"),("fedora","future"),
                ("gentoo","current"),("gentoo","future"),
                ("opensuse","current"),("opensuse","future"),("opensuse","experimental"),
                ("sabayon","current"),("sabayon","future"),
                ("slackware","current"),("slackware","future"),
                ("ubuntu","current"),("ubuntu","future")
]
def pkg(request, pkg):
  ps = PackageStats(pkg)
  s = DataStats()
  return render_to_response('pkg.html',
    {"stats": s,
    "pkg_stats":map(lambda x: ps.for_distro(*x),STAT_DISTROS),
    "name" : pkg
    }
  )
