from  Utilities import *
from Product import CurrencyPair, PriceTimestamp
import pandas as pd
import time 
from websocket import WebSocketApp
from json import dumps, loads
from pprint import pprint


class Exchange(object):
    def __init(self):
        return
    def GetPrice(self,symbol):
        raise NotImplementedError
        
class GDAX(Exchange):
    def __init__(self,CurrencyPair):
        self.URL = "wss://ws-feed.gdax.com"
        self.CurrencyPair = CurrencyPair
        
    def on_message(self,_, message):
        """Callback executed when a message comes.

        Positional argument:
        message -- The message itself (string)
        """
        JSONmessage =(loads(message))
        print (JSONmessage["price"])
        
    def on_error(ws, error):
        print("price could not be retrieved \n ", error)


    def on_open(self,socket):
        """Callback executed at socket opening.

        Keyword argument:
        socket -- The websocket itself
        """

        params = {
            "type": "subscribe",
            "product_ids": [self.GDAXstr(self.CurrencyPair)],
            "channels": ["ticker"]
        }
        socket.send(dumps(params))
        return

    def GDAXstr(self,CurrencyPair):
        return CurrencyPair.baseCurrency+"-"+CurrencyPair.quoteCurrency
    
    def __str__(self):
        return "GDAX"

    def streamPrices(self):
      
        ws = WebSocketApp(self.URL, on_open=self.on_open, on_message=self.on_message)
        ws.run_forever()
        
    def GetData(self,CurrencyPair):
        symbol = self.GDAXstr(CurrencyPair)
        urlg = "https://api.gdax.com/products/"+symbol+"/ticker"
        decodedatag = scrapeurl(urlg)
        return decodedatag
    

    def GetPriceTimestamp(self,CurrencyPair,precision =4):
        data = self.GetData(CurrencyPair)
        timestamp = data['time']
        gdaxprice = round(float(data['price']),precision)
        return PriceTimestamp(gdaxprice,timestamp)

class CryptoCompare(Exchange):
    
    def __str__(self):
        return "CryptoCompare"
    
    def GetPriceTimestamp(self,CurrencyPair,precision =4):
        price      =  self.GetPrice(CurrencyPair)
        timestamp  =  pd.to_datetime(time.time(),unit="s")
        return PriceTimestamp(price,timestamp)
        
    def GetPrice(self,CurrencyPair):
        urlg ="https://min-api.cryptocompare.com/data/price?fsym="+CurrencyPair.baseCurrency+"&tsyms="+CurrencyPair.quoteCurrency
        decodedata = scrapeurl(urlg)
        return decodedata[CurrencyPair.quoteCurrency]
    
    
    
    
    
    
    