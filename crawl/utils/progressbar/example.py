# -*- coding: utf-8 -*-
# Copyright: 2009 Nadia Alramli
# License: BSD

from progressbar import ProgressBar
import time
p = ProgressBar()
for i in range(101):
    p.render(i, 'step %s' % i)
    time.sleep(0.05)

p = ProgressBar('green', width=20, block='▣', empty='□')
for i in range(101):
    p.render(i, 'step %s\nProcessing...\nDescription: write something.' % i)
    time.sleep(0.05)
