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

def process_symbol(net, symbol):
 print "processing ", symbol
 #zuerst train_data prüfen, wenn keine Trainingsdaten da sind, dann brauchen wir nicht weitermachen
 train_data = load(symbol+'.train')
 if (len(train_data) == 0):
  print "--no training data, skip", symbol
  return
 print "-traing data loaded"
 data = load_stockdata(symbol)
 if (len(data) == 0):
  print "--no data, skip", symbol
  return
 print "-stock data loaded"
 settings = load_settings(symbol,data)
 if(len(settings) == 0):
  print "--no settings, skip", symbol
  return
 print "-settings loaded"
 #jetzt sind alle Daten vorhanden
 ds = build_dataset(data, train_data, settings)
 print "-train"
 trainer = BackpropTrainer(net, ds)
 trainer.trainEpochs(epochs)
 print "-saving network"
 NetworkWriter.writeToFile(net, 'network.xml') 
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
   dict[line['Date']] = line
  if (len(dict)>0):
   with open(fn, 'w') as fp:
    json.dump(dict, fp)
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
  for line in data:
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


def build_dataset(data, train_data, settings):
 ds = SupervisedDataSet(3, 3)
 keylist = data.keys()
 keylist.sort()
 for key in keylist:
  line = data[key]
  date = line['Date']
  wd = datetime.datetime.strptime(date,"%Y-%m-%d").weekday()
  op = (0.0,0.0,0.0)
  cl = float(line['Close'])/(settings['maxc']*2.0)
  vol = float(line['Volume'])/(settings['maxv']*2.0)
  if train_data.has_key(date):
   action = train_data[date]
   if(action=='IK'):
    op = (1.0,0.0,0.0)
   elif(action=='K'):
    op = (0.0,1.0,0.0)
   elif(action=='V'):
    op = (0.0,0.0,1.0)
  #input berechnen
  if vol>0.0:
   inp = (wd/6,cl,vol)
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
 if os.path.exists('network.xml'):
  net = NetworkReader.readFrom('network.xml')
 else:
  net = buildNetwork(3,3,3, hiddenclass=SigmoidLayer,outclass=LinearLayer, bias=True, outputbias=False, recurrent=False)
 for symbol in symbols:
  net = process_symbol(net, symbol)
  #das netzwerk wird nach jedem training gesichert
 print "all symbols processed, waiting 60 seconds to restart"
 for i in range(1,60):
  stdout.write("\r%d" % (60-i))
  stdout.flush()
  time.sleep(1)
 stdout.write("\n")
 break
#Netzwerk zusammenbauen oder laden
#net = buildNetwork(3,6,3, hiddenclass=SigmoidLayer,outclass=LinearLayer, bias=True, outputbias=False, recurrent=True)

#yahoo.get_price() 
#yahoo.get_trade_datetime() 

#echtdaten 
#ts = UnsupervisedDataSet(2,) 
#tS.addSample((wd,kurs),) 
#[ int(round(i)) for i in net.activateOnDataset(ts)[0]] 
