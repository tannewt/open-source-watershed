from timeline import *
from datetime import datetime
import traceback

passed = 0
tests = 0

def equal(v1, v2):
  if v1 == v2:
    return True
  else:
    print v1,"!=",v2
    return False

def run_test(f, test_name):
  global tests, passed
  tests += 1
  try:
    if f():
      passed += 1
      print "PASS:",test_name
    else:
      print "FAIL:",test_name
  except Exception, e:
    print "ERR :",test_name
    traceback.print_exc()
  print

print "Timeline"

# test equality
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  t2 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,15),1)])
  if equal(True,(t1==t2)) and equal(False,(t1==t3)):
    return True
  return False

run_test(test, "Equality")

# test get
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  if equal(1,t1[datetime(2009,1,14)]) and equal(None,t1[datetime(2009,1,16)]) and equal(None,t1[datetime(2009,1,14,12)]):
    return True
  return False

run_test(test, "Get")

# test insert
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  t2 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2),
                 (datetime(2009,1,16),3)])
  t1[datetime(2009,1,16)] = 3
  if equal(3,t1[datetime(2009,1,16)]) and equal(True,t1==t2):
    return True
  return False

run_test(test, "Insert")

# test set
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  t2 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),5)])
  t1[datetime(2009,1,15)] = 5
  if equal(5,t1[datetime(2009,1,15)]):
    return True
  return False

run_test(test, "Set")

# test slice
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2),
                 (datetime(2009,1,16),3)])
  t2 = Timeline([(datetime(2009,1,15),2),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,16),3)])
  if equal(t2,t1[datetime(2009,1,15):]) and equal(t3,t1[-1:]):
    return True
  return False

run_test(test, "Slice")

# test delete
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2)])
  t2 = Timeline([(datetime(2009,1,14),1)])
  del t1[datetime(2009,1,15)]
  if equal(t1,t2):
    return True
  return False

run_test(test, "Delete")

# test basic addition
  # test standard
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t2 = Timeline([(datetime(2009,1,15),2)])
  t3 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2),
                 (datetime(2009,1,16),3)])
  tr = t1 + t2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Simple Add")

  # test reverse
  # test self modifying
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t2 = Timeline([(datetime(2009,1,15),2)])
  t3 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),2),
                 (datetime(2009,1,16),3)])
  t1 += t2
  if equal(t3,t1):
    return True
  return False

run_test(test, "Self Add")
# test multiplication
  # test standard
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,16),6)])
  tr = t1*2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Standard Multiply")
  # test reverse
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,16),6)])
  tr = 2*t1
  if equal(t3,tr):
    return True
  return False

run_test(test, "Reverse Multiply")
  # test self modifying
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,16),6)])
  t1 *= 2
  if equal(t3,t1):
    return True
  return False

run_test(test, "Self Multiply")
# test division
  # test standard
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,16),6)])
  tr = t3/2
  if equal(t1,tr):
    return True
  return False

run_test(test, "Standard Division")
  # test self modifying
def test():
  t1 = Timeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t3 = Timeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,16),6)])
  t3/=2
  if equal(t1,t3):
    return True
  return False

run_test(test, "Self Division")

print
print "StepTimeline"

# test get
def test():
  t1 = StepTimeline([(datetime(2009,1,14),1),
                     (datetime(2009,1,16),2)])
  if equal(1,t1[datetime(2009,1,15)]) and equal(1,t1[datetime(2009,1,14)]):
    return True
  return False

run_test(test, "Get")

# test basic addition
  # test standard
def test():
  t1 = StepTimeline([(datetime(2009,1,14),1),
                     (datetime(2009,1,16),3)])
  t2 = StepTimeline([(datetime(2009,1,15),2)])
  t3 = StepTimeline([(datetime(2009,1,14),1),
                     (datetime(2009,1,15),3),
                     (datetime(2009,1,16),5)])
  tr = t1 + t2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Simple Add")

  # test reverse
  # test self modifying
  # not reasonable

# test multiplication
  # test standard
def test():
  t1 = StepTimeline([(datetime(2009,1,14),4),
                     (datetime(2009,1,16),3)])
                 
  t2 = StepTimeline([(datetime(2009,1,14),2),
                     (datetime(2009,1,15),4),
                     (datetime(2009,1,16),3)])
                 
  t3 = StepTimeline([(datetime(2009,1,14),8),
                     (datetime(2009,1,15),16),
                     (datetime(2009,1,16),9)])
  tr = t1*t2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Standard Multiply")
  # test self modifying
  # not reasonable

# test division
  # test standard
def test():
  t1 = StepTimeline([(datetime(2009,1,14),4),
                     (datetime(2009,1,16),3)])
                 
  t2 = StepTimeline([(datetime(2009,1,14),2),
                     (datetime(2009,1,15),4),
                     (datetime(2009,1,16),3)])
                 
  t3 = StepTimeline([(datetime(2009,1,14),8),
                     (datetime(2009,1,15),16),
                     (datetime(2009,1,16),9)])
  t4 = StepTimeline([(datetime(2009,1,14),4),
                     (datetime(2009,1,15),4),
                     (datetime(2009,1,16),3)])
  tr = t3/t2
  tr2 = t3/t1
  if equal(t4,tr) and equal(t2,tr2):
    return True
  return False

run_test(test, "Standard Division")
  # test self modifying
  # not reasonable

print
print "ConnectedTimeline"

# test get
def test():
  t1 = ConnectedTimeline([(datetime(2009,1,14),1),
                          (datetime(2009,1,16),3)])
  if equal(2.0,t1[datetime(2009,1,15)]):
    return True
  return False

run_test(test, "Get")

# test basic addition
  # test standard
def test():
  t1 = ConnectedTimeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,16),3)])
  t2 = ConnectedTimeline([(datetime(2009,1,15),2)])
  t3 = ConnectedTimeline([(datetime(2009,1,14),1),
                 (datetime(2009,1,15),4),
                 (datetime(2009,1,16),5)])
  tr = t1 + t2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Simple Add")

  # test reverse
  # test self modifying
  # not reasonable

# test multiplication
  # test standard
def test():
  t1 = ConnectedTimeline([(datetime(2009,1,14),4),
                 (datetime(2009,1,16),2)])
                 
  t2 = ConnectedTimeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,15),4),
                 (datetime(2009,1,16),3)])
                 
  t3 = ConnectedTimeline([(datetime(2009,1,14),8),
                 (datetime(2009,1,15),12.0),
                 (datetime(2009,1,16),6)])
  tr = t1*t2
  if equal(t3,tr):
    return True
  return False

run_test(test, "Standard Multiply")
  # test self modifying
  # not reasonable
# test division
  # test standard
def test():
  t1 = ConnectedTimeline([(datetime(2009,1,14),4),
                 (datetime(2009,1,15),3),
                 (datetime(2009,1,16),3)])
                 
  t2 = ConnectedTimeline([(datetime(2009,1,14),2),
                 (datetime(2009,1,15),4),
                 (datetime(2009,1,16),3)])
                 
  t3 = ConnectedTimeline([(datetime(2009,1,14),8),
                 (datetime(2009,1,15),12),
                 (datetime(2009,1,16),9)])
  tr = t3/t2
  tr2 = t3/t1
  if equal(t1,tr) and equal(t2,tr2):
    return True
  return False

run_test(test, "Standard Division")
  # test self modifying
  # not reasonable

print
if passed==tests:
  print "All tests PASSED!"
else:
  print "Passed",passed,"of",tests,"tests."
