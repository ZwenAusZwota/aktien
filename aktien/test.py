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
 for key in keylist:
  line = data[key]
  c = float(line['Close'] )/ (2.0 * settings['maxc'])
  v = float(line['Volume'] )/ (2.0 * settings['maxv'])
  d = line['Date']
  wd = datetime.datetime.strptime(d,"%Y-%m-%d").weekday()/6.0
  ret = net.activate([wd,c,v])
  if (train.has_key(d)):
   print d, train[d], ret

 
############################################

print "starting process. exit with CTRL+C"

sym_file = 'symbols.json'

signal.signal(signal.SIGINT, signal_handler)
#signal.pause()

while True:
 print "loading symbols"
 symbols = load(sym_file)
 if os.path.exists('network.xml'):
  print "loading network"
  net = NetworkReader.readFrom('network.xml')
 else:
  print "waiting for network"
  time.sleep(60)
  continue
 for symbol in symbols:
  print symbol
  process_symbol(net, symbol)
 #break
 print "all symbols processed, waiting 10 seconds to restart"
 time.sleep(60)

#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
