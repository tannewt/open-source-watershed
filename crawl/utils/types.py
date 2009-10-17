# -*- coding: utf-8 -*-
class Repo:
	def __init__(self):
		self.id = None
		self.distro_id = None
		self.codename = None
		self.component = None
		self.architecture = None
		self.last_crawl = None
	
	def __str__(self):
		return " ".join(map(str, (self.codename, self.component, self.architecture)))

class Release:
	def __init__(self):
		self.package = None
		self.version = None
		self.revision = 0
		self.released = None
	
	def __str__(self):
		return " ".join(map(str, (self.package, self.version, self.revision, self.released)))
	
	def __repr__(self):
		return self.__str__()

class UpstreamRelease(Release):
	def __init__(self):
		Release.__init__(self)
		self.source = None

class DownstreamRelease(Release):
	def __init__(self):
		Release.__init__(self)
		self.repo_id = None

class User:
	def __init__(self):
		self.username = None
		self.level = None
		self.reviews = None
		self.points = None