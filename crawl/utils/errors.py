# -*- coding: utf-8 -*-
class UnknownDistroError(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

class UnknownPackageError(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

class LinkCycleError(Exception):
        def __init__(self, value):
                self.value = value

        def __str__(self):
                return repr(self.value)
