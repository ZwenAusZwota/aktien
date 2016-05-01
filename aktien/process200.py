#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import time
from pybrain.tools.xml.networkreader import NetworkReader
from stock_functions import *


url = "http://aktien.zwen-aus-zwota.de/update.php"
method = "POST"
handler = urllib2.HTTPHandler()
opener = urllib2.build_opener(handler)

symbols = load_file("symbols.json")
net = NetworkReader.readFrom('net200.xml')
for symbol in symbols:
 print symbol
 settings = load_file(symbol+'.set')
 y = yahoo_get_200(symbol)
 if len(y)!=200:
  continue
 #200tage vefügbar
 inp = []
 for line in y:
  cl = float(line['Close'])/(settings['maxc']*2.0)
  vol = float(line['Volume'])/(settings['maxv']*2.0)
  inp.append(cl)
  inp.append(vol)
 ret = net.activate(inp)
 a = 'IK'
 v = ret[0]
 if ret[0]<ret[1]:
  a = 'K'
  v = ret[1]
 if ret[2]>ret[1]:
  a = 'V'
  v = ret[2]
 #date = time.strftime("%Y-%m-%d")
 date = y[199]['Date']
 dict = {"date":date,"symbol":symbol,"action":a,"value":v}
 request = urllib2.Request(url, data = urllib.urlencode(dict))
 request.add_header("Content-Tpye", "application/json")
 request.get_method = lambda: method
 try:
  connection = opener.open(request)
 except urllib2.HTTPError ,e:
  connection = e
 if connection.code == 200:
  data = connection.read()
  print data
 else:
  print "error", connection
