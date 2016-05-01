#/usr/bin/python
# -*- coding: utf-8 -*-
import datetime 
import json
import os.path
import signal
import sys
import time
from yahoo_finance import Share
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import *
from pybrain.datasets import UnsupervisedDataSet
from pybrain.tools.xml.networkreader import NetworkReader
# Eingabe Aktien-Symbol
# prüfen, ob TRAIN-Datei vorhanden
# YAHOO-Daten laden und in DATA-Datei schreiben
# ermitteln der Signale, in TRAIN-Datei schreiben 


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
 data = load_stockdata(symbol)
 if len(data) == 0:
  print "no data"
  return
 settings = load_settings(symbol)
 if len(settings) == 0:
  print "no settings"
  return
 keylist = data.keys()
 keylist.sort()
 dict = {}
 for j in range(200,len(keylist)-1):
  idx_to = j
  idx_fr = j-200
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
  dict[key] = a
 if (len(dict)>0):
  with open(symbol+'.train', 'w') as fp:
   json.dump(dict, fp)

def load_stockdata(symbol):
 print "loading stock data"
 fn = symbol+'.data'
 fn_set = symbol+'.set'
 data = load(fn)
 if len(data) > 0: 
  return data
 #finanzdaten laden, feld umkehren
 yahoo = Share(symbol)
 from_date = '2000-01-01'
 to_date = '2015-12-31'
 data = yahoo.get_historical(from_date, to_date)
 data.reverse()
 dict = {}
 maxc = 0.0
 minc = 100000.0
 maxv = 0.0
 minv = 99999999.0
 for line in data:
  if int(line['Volume']) > 0:
   dict[line['Date']] = line
   c = float(line['Close'])
   v = float(line['Volume'])
   maxc = max(maxc, c)
   minc = min(minc, c)
   maxv = max(maxv, v)
   minv = min(minv, v)
 if (len(dict)>0):
  with open(fn, 'w') as fp:
   json.dump(dict, fp)
  settings = {"maxc":maxc,"minc":minc,"maxv":maxv,"minv":minv}
  with open(fn_set, 'w') as fp:
   json.dump(settings, fp)
  data = dict
 return data

def load_settings(symbol):
 fn = symbol+'.set'
 if(os.path.exists(fn)):
  with open(fn,'r') as f:
   settings = json.load(f)
 return settings

############################################

print "starting process. exit with CTRL+C"

sym_file = 'symbols.json'
net_file = 'net200.xml'
signal.signal(signal.SIGINT, signal_handler)
#signal.pause()


sym = raw_input('Symbol:')

if sym != '':
 symbol = sym.strip()
 print "loading network"
 net = NetworkReader.readFrom(net_file)
 process_symbol(net, symbol)
 print 'symbol processed'
#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
