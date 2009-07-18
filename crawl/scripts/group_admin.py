# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from utils.db import groups

if len(sys.argv)==1:
	print sys.argv[0],"<cmd>","[opts]"
	print "list"
	print "list <group>"
	print "create <name>"
	print "delete <name>"
	print "add_to <group> <package>"
elif sys.argv[1]=="list" and len(sys.argv)==2:
	gs = groups.list_groups()
	for group in gs:
		print group
elif sys.argv[1]=="list":
	pkgs = groups.get_group(sys.argv[2])
	for p in pkgs:
		print p
elif sys.argv[1]=="create":
	print "new group id:",groups.create_group(sys.argv[2])
elif sys.argv[1]=="delete":
	groups.delete_group(sys.argv[2])
elif sys.argv[1]=="add_to":
	groups.add_to_group(sys.argv[3], sys.argv[2])
print "done"