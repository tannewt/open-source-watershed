# -*- coding: utf-8 -*-
from django.http import HttpResponse
from utils.history import *

def package(request):
	if "package" not in request.GET or "cb" not in request.GET:
		return HttpResponse(status=400)
	p = request.GET["package"]
	try:
		ph = PackageHistory(p)
	except UnknownPackageError:
		return HttpResponse(status=400)
	distros = get_all_distros([ph], "current")
	cb = request.GET["cb"]
	response = cb+'({"package":"%s","latest":"%s","distros":['%(ph.name, ph.get_greatest_timeline()[-1])
	distro_entries = []
	for distro in distros:
		timeline = distro.get_obsoletion_timeline()
		v = distro.get_pkg(ph.name)[-1]
		if v=='0':
			v = "--"
		if len(timeline)>0 and timeline[-1]==0.0:
			utd = "true"
		else:
			utd = "false"
		distro_entries.append('{"logo": "%s.png", "version": "%s", "uptodate": %s}'%(distro.name, v, utd))
	response += ",".join(distro_entries)+ "]})"
	return HttpResponse(response)
