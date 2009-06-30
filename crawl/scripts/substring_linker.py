# -*- coding: utf-8 -*-
# link evaluator
import difflib
import sys
import random

sys.path.append(".")
from utils import history

if len(sys.argv)>1:
	targets = sys.argv[1:]

pkgs = history.get_all(False)
print len(pkgs)
#pkgs = random.sample(pkgs, 10000)

JUNK = ["-dev", "-dbg", "-devel"]

CLEANED = []
for i in range(len(pkgs)):
	for s in JUNK:
		if pkgs[i].endswith(s):
			CLEANED.append(pkgs[i].strip(s))
			break

histories = {}
for i in range(len(targets)):
	ph = history.PackageHistory(targets[i], 256)
	histories[targets[i]] = ph.timeline.values()

seq = difflib.SequenceMatcher()
vseq = difflib.SequenceMatcher()
for w1 in targets:
	row = [w1]
	seq.set_seq2(w1)
	vseq.set_seq2(histories[w1])
	for w2 in pkgs:
		seq.set_seq1(w2)
		l = float(seq.find_longest_match(0, len(w2)-1, 0, len(w1)-1)[-1])
		score = l/len(w1) + l/len(w2)
		if w1 in w2:
			print w2, score
		
		if score < 0.8:
			continue
		
		if w2 not in histories:
			ph = history.PackageHistory(w2, 256)
			histories[w2] = ph.timeline.values()
		vseq.set_seq1(histories[w2])
		vscore = vseq.ratio()
	
		if  vscore<0.2:
			row.append("")
		else:
			print w1,"<->",w2,score,vscore