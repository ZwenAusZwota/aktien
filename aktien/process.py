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
from yahoo_finance import Share

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
 yahoo = Share(symbol)
 mp = 2.0*settings['maxc']
 p = float(yahoo.get_price())/mp 
 d = yahoo.get_trade_datetime()
 wd = datetime.datetime.strptime(d[:10],"%Y-%m-%d").weekday()/6.0 
 v = float(yahoo.get_volume())/(2*settings['maxv'])
 ts = UnsupervisedDataSet(3,) 
 ts.addSample((wd,p,v),)
 ret = net.activate([wd,p,v])
 print "IK, K, V ", ret

 
############################################

print "starting process. exit with CTRL+C"

sym_file = 'symbols.json'

signal.signal(signal.SIGINT, signal_handler)
#signal.pause()

while True:
 print "loading symbols"
 symbols = load(sym_file)
 print "loading network"
 net = NetworkReader.readFrom('network.xml')
 for symbol in symbols:
  process_symbol(net, symbol)
 break
 print "all symbols processed, waiting 10 seconds to restart"
 time.sleep(10)

#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
