from yahoo_finance import Share
import time
import os.path
import json
from datetime import date, timedelta

def load_file(fn):
 if os.path.exists(fn):
  with open(fn, 'r') as f:
   return json.load(f)
 else:
  return []

def yahoo_get_price(symbol):
 yahoo = Share(symbol)
 price = yahoo.get_price()
 trade_date = yahoo.get_trade_datetime()
 dict={"p":price,"d":trade_date}
 return dict

def yahoo_get_200(symbol):
 yahoo = Share(symbol)
 fd = date.today() - timedelta(365)
 from_date = fd.strftime('%Y-%m-%d')
 to_date = time.strftime('%Y-%m-%d')
 data = yahoo.get_historical(from_date, to_date)
 if len(data) < 200:
  return
 d2 = []
 for i in range(0,200):
  d2.append(data[i])
 print len(d2)
 d2.reverse()
 return d2
