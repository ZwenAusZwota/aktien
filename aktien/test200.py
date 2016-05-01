#/usr/bin/python
# -*- coding: utf-8 -*-
import datetime 
import json
import os.path
import signal
import sys
import time
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import *
from pybrain.datasets import UnsupervisedDataSet
from pybrain.tools.xml.networkreader import NetworkReader

def load(fn):
 if os.path.exists(fn):
  with open(fn, 'r') as f:
   return json.load(f)
 else:
  return []

def signal_handler(signal, frame):
 print ''
 print 'stopping...'
 sys.exit(0)

def process_symbol(net, symbol):
 settings = load(symbol+'.set')
 if(len(settings)==0):
  return
 train = load(symbol+'.train')
 if len(train)==0:
  return
 data = load(symbol+'.data')
 if len(data) == 0:
  return
 keylist = data.keys()
 keylist.sort()
 for date, action in train.iteritems():
  idx_to = keylist.index(date)
  idx_fr = idx_to - 200
  if idx_fr < 0:
   idx_fr = 0  
  inp = []
  for i in range(idx_fr,idx_to):
   key = keylist[i]
   line = data[key]
   cl = float(line['Close'])/(settings['maxc']*2.0)
   vol = float(line['Volume'])/(settings['maxv']*2.0)
   inp.append(cl)
   inp.append(vol)
  ret = net.activate(inp)
  a = 'IK'
  if ret[0]<ret[1]:
   a = 'K'
  if ret[2]>ret[1]:
   a = 'V'
  print date, action, a

 
############################################

print "starting process. exit with CTRL+C"

sym_file = 'symbols.json'
net_file = 'net200.xml'
signal.signal(signal.SIGINT, signal_handler)
#signal.pause()

while True:
 print "loading symbols"
 symbols = load(sym_file)
 if os.path.exists(net_file):
  print "loading network"
  net = NetworkReader.readFrom(net_file)
 else:
  print "waiting for network"
  time.sleep(60)
  continue
 for symbol in symbols:
  print symbol
  process_symbol(net, symbol)
 break
 print "all symbols processed, waiting 10 seconds to restart"
 time.sleep(10)

#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
