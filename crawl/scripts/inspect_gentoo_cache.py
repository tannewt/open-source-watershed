import cPickle as pickle

f = open("files/gentoo/cache.pickle")

cache = pickle.load(f)
f.close()

for k in cache.keys():
  for b in cache[k]:
    print b,k,len(cache[k][b]),"releases"
    for p in cache[k][b]:
      print "\t",p[0],p[1],p[-2]
    print
