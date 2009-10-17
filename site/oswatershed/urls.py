# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
		# Example:
		(r'^$', 'oswatershed.views.index'),
		(r'^$', 'oswatershed.views.home'),
		(r'^distro/(?P<distro>[^/]+)/?$', 'oswatershed.views.distro'),
		(r'^pkg/(?P<pkg>[^/]+)/?$', 'oswatershed.views.pkg'),
		(r'^search2/(?P<search>[^/]+)/?$', 'oswatershed.views.search2'),
		(r'^search/(?P<search>[^/]+)/?$', 'oswatershed.views.search'),
		(r'^group/(?P<group>[^/]+)/?$', 'oswatershed.views.pkg_set'),
		(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': 'http://static.oswatershed.org/favicon.ico'}),


		# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
		# to INSTALLED_APPS to enable admin documentation:
		# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

		# Uncomment the next line to enable the admin:
		# (r'^admin/(.*)', admin.site.root),
)
