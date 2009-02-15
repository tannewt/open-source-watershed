import sys

if len(sys.argv) < 3:
  print sys.argv[0] + " <mirror> <file of files>"
  sys.exit(-1)

mirror = sys.argv[1]
fs = sys.argv[2]

files = open(fs)

ENDS = []
LIVEENDS = []
for fn in files:
  path = fn.replace(mirror,"")
  bits = path.strip().split("/")
  live = bits[-1].endswith((".tar.gz",".tar.bz2",".tgz"))
  for bit in bits[:-1]:
    if bit not in ENDS:
      ENDS.append(bit)
    if live and bit not in LIVEENDS:
      LIVEENDS.append(bit)

for end in ENDS:
  if end not in LIVEENDS:
    print end
