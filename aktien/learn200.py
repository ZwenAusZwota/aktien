#/usr/bin/python
# -*- coding: utf-8 -*-
import datetime 
import json
import os.path
import signal
import sys
import time
from sys import stdout
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import *
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.tools.xml.networkreader import NetworkReader
from yahoo_finance import Share
#in der DB bereits die Aktionen mit Datum hinterlegen 
#dazu eingabemaske: Symbol, Datum, Aktion 
#gespeichert werden soll so: 
#angegebener Tag: Symbol, Datum, Aktionshinweis 
#Folgetag 1: Symbol, Datum+1, Aktion 
#Folgetag 2: Symbol, Datum+2, Aktion 

#lernen Mittels rekkurentem Netzwerk 
#Eingabe: Wochentag, Schlußkurs 
#Ausgabe: InfoKauf, Kauf, Verkauf

epochs = 1000
network_file = 'net200.xml'

######################## 
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

def process_symbol(ds, symbol):
 data = load_stockdata(symbol)
 if (len(data) == 0):
  print "--no data, skip", symbol
  return ds
 settings = load_settings(symbol,data)
 if(len(settings) == 0):
  print "--no settings, skip", symbol
  return ds
 train_data = load(symbol+'.train')
 if (len(train_data) == 0):
  print "--no training data, skip", symbol
  return ds
 #jetzt sind alle Daten vorhanden
 ds = build_dataset(ds, data, train_data, settings)
 return ds

def train(net,ds):
 trainer = BackpropTrainer(net, ds)
 #for i in range(0,epochs):
 # print trainer.train()
 #trainer.trainEpochs(epochs)
 print "-e", trainer.train()
 #trainer.trainUntilConvergence()
 trainer.trainEpochs(epochs)
 print "-e", trainer.train()
 print "-saving network"
 NetworkWriter.writeToFile(net, network_file)
 return net

def load_stockdata(symbol):
 fn = symbol+'.data'
 data = load(fn)
 if (len(data) == 0):
  print "no data, loading yahoo", symbol
  #finanzdaten laden, feld umkehren
  yahoo = Share(symbol)
  from_date = '2000-01-01'
  to_date = '2015-12-31'
  data = yahoo.get_historical(from_date, to_date)
  data.reverse()
  dict = {}
  for line in data:
   if int(line['Volume']) > 0:
    dict[line['Date']] = line
  if (len(dict)>0):
   with open(fn, 'w') as fp:
    json.dump(dict, fp)
   data = dict
 return data

def load_settings(symbol, data):
 fn = symbol+'.set'
 if(os.path.exists(fn)):
  with open(fn,'r') as f:
   settings = json.load(f)
 else:
  maxc = 0.0
  minc = 100000.0
  maxv = 0.0
  minv = 99999999.0
  keylist = data.keys()
  for key in keylist:
   line = data[key]
   c = float(line['Close'])
   v = float(line['Volume'])
   maxc = max(maxc, c)
   minc = min(minc, c)
   maxv = max(maxv, v)
   minv = min(minv, v)
  settings = {"maxc":maxc,"minc":minc,"maxv":maxv,"minv":minv}
  with open(fn, 'w') as fp:
   json.dump(settings, fp)
 return settings


def build_dataset(ds, data, train_data, settings):
 #ds = SupervisedDataSet(400, 3)
 keylist = data.keys()
 keylist.sort()
 for i in range(200,len(keylist)):
  date = keylist[i]
  line = data[date]
  op = (0.0,0.0,0.0)
  if date in train_data:
   action = train_data[date]
 #for date, action in train_data.iteritems():
  #idx_to = -1
   if(action=='IK'):
    op = (1.0,0.0,0.0)
   elif(action=='K'):
    op = (0.0,1.0,0.0)
   elif(action=='V'):
    op = (0.0,0.0,1.0)
  idx_to = keylist.index(date)
  idx_fr = idx_to - 200
  if idx_fr < 0:
   idx_fr = 0
  inp = []
  for j in range(idx_fr,idx_to):
   key = keylist[j] 
   line = data[key]
   cl = float(line['Close'])/(settings['maxc']*2.0)
   vol = float(line['Volume'])/(settings['maxv']*2.0)
   inp.append(cl)
   inp.append(vol)
  ds.addSample(inp,op)
 return ds

############################################

print "starting process. exit with CTRL+C"

sym_file = 'symbols.json'

signal.signal(signal.SIGINT, signal_handler)
#signal.pause()

while True:
 print "loading symbols"
 symbols = load(sym_file)
 print "loading network"
 if os.path.exists(network_file):
  net = NetworkReader.readFrom(network_file)
 else:
  #net = buildNetwork(400,10,3, hiddenclass=SigmoidLayer,outclass=LinearLayer, bias=True, outputbias=False, recurrent=False)
  net = buildNetwork(400,100,10,3, hiddenclass=TanhLayer,outclass=LinearLayer, bias=True, outputbias=False, recurrent=False)
 ds = SupervisedDataSet(400, 3)
 for symbol in symbols:
  print symbol
  ds = process_symbol(ds, symbol)
 net = train(net,ds)
  #das netzwerk wird nach jedem training gesichert
 #print "all symbols processed"
 #break
 #print " waiting 60 seconds to restart"
 #for i in range(1,60):
 # stdout.write("\r%d " % (60-i))
 # stdout.flush()
 # time.sleep(1)
 #stdout.write("\n")
#Netzwerk zusammenbauen oder laden
#net = buildNetwork(3,6,3, hiddenclass=SigmoidLayer,outclass=LinearLayer, bias=True, outputbias=False, recurrent=True)

#yahoo.get_price() 
#yahoo.get_trade_datetime() 

#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
