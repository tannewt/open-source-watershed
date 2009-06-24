# -*- coding: utf-8 -*-
class Distro:
	def __init__(self):
		self.id = None

class Repo:
	def __init__(self):
		self.id = None
		self.distro = None
		self.codename = None
		self.component = None
		self.architecture = None

class Release:
	def __init__(self):
		self.package = None
		self.version = None
		self.revision = None
		self.released = None
	
	def __str__(self):
		return " ".join(map(str, (self.package, self.version, self.released)))

class UpstreamRelease(Release):
	def __init__(self):
		Release.__init__(self)
		self.source = None

class DownstreamRelease(Release):
	def __init__(self):
		Release.__init__(self)
		self.repo = None