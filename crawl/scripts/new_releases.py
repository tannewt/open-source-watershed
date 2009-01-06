import cPickle as pickle
import os
import datetime

targets = []

files = os.listdir("crawl_stats/")
files.sort()
for f in files:
  if f.endswith(".pickle"):
    print datetime.datetime.fromtimestamp(int(f.split(".")[0])),
    f = open("crawl_stats/"+f)
    data = pickle.load(f)
    d = {}
    for key,value in data:
      d[key] = value
    f.close()
    for k in d.keys():
      if k not in targets:
        targets.append(k)
    
    for t in targets:
      if t in d:
        print str(d[t])+"\t",
      else:
        print "  \t",
    print
        
        
