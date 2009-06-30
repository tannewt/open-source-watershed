import sys

f = open(sys.argv[1])
lines = f.readlines()
lines = filter(lambda x: x[0] != "#", lines)
pkgs = []
for i in range(len(lines)/2):
	#print lines[2*i:2*(i+1)]
	first = lines[2*i].strip().split("=")[1]
	second = lines[2*i + 1].strip().split("=")[1]
	if ";" in first and ";" not in second:
		pkg = second
		cat = first
	elif ";" not in first and ";" in second:
		pkg = first
		cat = second
	else:
		continue
	if pkg not in pkgs:
		pkgs.append(pkg)

for p in pkgs:
	print p
