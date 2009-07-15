# -*- coding: utf-8 -*-
import datetime

class VersionNode:
	def __init__(self,date=None):
		self.tokens = []
		self.children = {}
		self.date = date
	
	def add(self, date, tokens):
		if len(tokens) == 0:
			self.date = date
		else:
			if tokens[0] not in self.tokens:
				self.tokens.append(tokens[0])
				self.children[tokens[0]] = VersionNode()
			self.children[tokens[0]].add(date, tokens[1:])
	
	def next(self, tokens):
		"""Given a series of tokens return its release date and all subtrees with later versions."""
		if len(tokens)==0 or tokens[0] not in self.tokens:
			if len(tokens)>0 and len(self.tokens)>0 and type(tokens[0]) == type(self.tokens[-1]) and tokens[0] > self.tokens[-1]: 
				return (self.date,[])
			elif len(tokens)>0 and len(self.tokens)>0:
				date,children = self.children[self.tokens[0]].next([])
				return (date, children + map(lambda x: self.children[x], self.tokens[1:]))
			else:
				return (self.date,[])
		else:
			date,children = self.children[tokens[0]].next(tokens[1:])
			if date==None:
				date = self.date
			return (date,children + map(lambda x: self.children[x], self.tokens[self.tokens.index(tokens[0])+1:]))
	
	def after(self, date):
		c = map(lambda k: self.children[k].after(date),self.children)
		if len(c)>0:
			c = min(c)
		else:
			c = datetime.datetime(9999,12,31)
		
		if self.date!=None and self.date > date:
			return min(self.date, c)
		else:
			return c
	
	def count_after(self, date):
		c = sum(map(lambda k: self.children[k].count_after(date),self.children))
		if self.date!=None and (date==None or self.date > date):
			c += 1
		return c
	
	def _missing_max(t1, t2):
		if len(t1)==0:
			return 2
		if len(t2)==0:
			return 1
		
		if t1[0]==t2[0]:
			self._missing_max(t1[1:], t2[1:])
		elif t1[0]>t2[0]:
			return 1
		return 2
	
	def max(self, t1, t2):
		if len(t1)==0:
			return 2
		if len(t2)==0:
			return 1
		
		if t1[0]==t2[0]:
			if t1[0] in self.children:
				return self.children[t1[0]].max(t1[1:],t2[1:])
			else:
				return self._missing_max(t1[1:], t2[1:])
		else:
			if t1[0] in self.tokens and t2[0] in self.tokens:
				if self.tokens.index(t1[0]) < self.tokens.index(t2[0]):
					return 2
				else:
					return 1
			else:
				if t1[0] < t2[0]:
					return 2
				else:
					return 1
	
	def __str__(self, prefix="", indent=0):
		result = ["	"*indent + str(self.date)]
		for t in self.tokens:
			v = prefix + str(t)
			result.append("	"*indent + v)
			result.append(self.children[t].__str__(v, indent+1))
		return "\n".join(result)

class VersionTree:
	def __init__(self, timeline=None):
		self.root = VersionNode()
		if timeline!=None:
			for date in timeline:
				self.add_release(date, timeline[date])
	
	def add_release(self, date, version):
		self.root.add(date, self._tokenize(version))
	
	def get_date(self, version):
		return self.root.next(self._tokenize(version))[0]
	
	def max(self, v1, v2):
		if v1=="0":
			return v2
		if v2=="0":
			return v1
		
		i = self.root.max(self._tokenize(v1), self._tokenize(v2))
		if i==1:
			return v1
		else:
			return v2
	
	def compute_lag(self, date, version):
		d,newer = self.root.next(self._tokenize(version))
		if d==None:
			oldest_new = datetime.datetime(9999,12,31)
		else:
			if len(newer)>0:
				oldest_new = min(map(lambda r: r.after(d),newer))
			else:
				oldest_new = datetime.datetime(9999,12,31)
		
		if oldest_new != datetime.datetime(9999,12,31):
			return date - oldest_new
		else:
			return date - date
	
	def compute_obsoletions(self, date, version):
		d,newer = self.root.next(self._tokenize(version))
		return sum(map(lambda r: r.count_after(d),newer))
	
	def _tokenize(self, v):
		tokens = []
		token = v[0]
		num = v[0].isdigit()
		for c in v[1:]:
			if not c.isdigit() and not c.isalpha():
				if num:
					tokens.append(int(token))
				else:
					tokens.append(token)
				token = None
				num = None
			elif num == None:
				token = c
				if c.isdigit():
					num = True
				else:
					num = False
			elif num and not c.isdigit():
				tokens.append(int(token))
				token = c
				num = False
			elif not num and c.isdigit():
				tokens.append(token)
				token = c
				num = True
			else:
				token += c
		if num:
			tokens.append(int(token))
		else:
			tokens.append(token)
		
		return tokens
	
	def __str__(self):
		return str(self.root)

if __name__=="__main__":
	t = VersionTree()
	print t._tokenize("2.6.28.10")
	print t._tokenize("1.0_beta1")
	
	t.add_release(datetime.datetime(2009, 3, 1), "2.0")
	t.add_release(datetime.datetime(2009, 3, 2), "2.1")
	t.add_release(datetime.datetime(2009, 3, 3), "3.0")
	t.add_release(datetime.datetime(2009, 3, 4), "2.2")
	print t
	
	print "lag",t.compute_lag(datetime.datetime(2009, 3, 5), "2.1")
	print "obs",t.compute_obsoletions(datetime.datetime(2009, 3, 5), "2.1")
