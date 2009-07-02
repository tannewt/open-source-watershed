# -*- coding: utf-8 -*-
import datetime
import sys
sys.path.append(".")

from utils import helper
from utils import parsers
from utils.db import upstream

NAME="php"
source_id = upstream.source("php", "custom php crawler")

MIRROR="http://us3.php.net"

def print_helper(a,depth=0):
	#print type(a),a
	if type(a) == dict:
		for key in a:
			print_helper(key, depth+1)
			print_helper(a[key], depth+1)
	else:
		print "  "*depth+str(a)

def _deserialize(tokens):
	first = tokens.pop(0)
	result = None
	if first=="a":
		result = {}
		length = int(tokens.pop(0))
		for i in range(length):
			key = _deserialize(tokens)
			value = _deserialize(tokens)
			if type(key)!=dict:
				result[key] = value
		#print result
	elif first=="i":
		second = tokens.pop(0)
		result = int(second)
	elif first=="s":
		tokens.pop(0)
		result = tokens.pop(0)
	elif first=="b":
		second = tokens.pop(0)
		result = second=="1"
	else:
		print first
	return result

def deserialize(s):
	s = s.replace("{","")
	s = s.replace("}","")
	s = s.replace(";",":")
	s = s.split("\"")
	split = []
	i = 0
	while i < len(s):
		split += s[i].strip(":").split(":")
		try:
			split.append(s[i+1])
		except:
			pass
		i += 2
	return _deserialize(split)

def flatten(d):
	if type(d) == dict:
		date = None
		filename = None
		result = []
		for key in d:
			value = d[key]
			if key=="date":
				try:
					date = datetime.datetime.strptime(value,"%d %B %Y")
				except:
					date = datetime.datetime.strptime(value,"%d %b %Y")
			elif key=="filename":
				filename = value
			else:
				r = flatten(value)
				if r != None:
					result += r
		if date!=None:
			for i in range(len(result)):
				if result[i][0]==None:
					result[i][0] = date
		if filename!=None:
			result.append([date,filename])
		if len(result)==0:
			return None
		return result

def get_releases(last_crawl=None):
	pkgs = []
	for version in range(4,8):
		fn = "files/helper/php%d.txt"%version
		helper.open_url(MIRROR+"/releases/index.php?serialize=1&version=%d&max=3000"%version,fn)
		f = open(fn)
		s = f.read()
		f.close()

		d = deserialize(s)
		f = flatten(d)
		if f == None: #no filenames found
			continue
		
		for date,fn in f:
			rel = parsers.parse_filename(fn)
			if rel!=None and "pl" not in rel.version:
				rel.released = date
				pkgs.append(rel)
	return pkgs

def crawl():
	print "php"
	last_crawl = upstream.last_crawl(source_id)
	rels = get_releases(last_crawl)
	count, max_date = upstream.add_releases(source_id, rels)
	print "\t"+str(count),"new releases"
	upstream.set_last_crawl(source_id, max_date)

if __name__=="__main__":
	pkgs = get_releases()
	for p in pkgs:
		print p