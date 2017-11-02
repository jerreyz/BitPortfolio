from  Utilities import *
from Product import CurrencyPair, PriceTimestamp
import pandas as pd
import time 
from websocket import WebSocketApp
from json import dumps, loads
from pprint import pprint
from bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep
from util.setup_logger import setup_logger
import os
import csv
from ipywidgets import widgets


class WebsocketConnection(object):
    def __init(self):
                raise NotImplementedError

    def GetPrice(self,symbol):
        raise NotImplementedError
        
    def setup_logger(self):
        # Prints logger info to terminal
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
        ch = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to ch
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger    
    
    def SaveTimeSeries(self,location = "/Users/jeroenderyck/Documents/Data/CryptoPrices/"):
        path = os.path.join(location, '%s_%s.csv' % (self.ExchangeName, self.ticker))
        self.TimeSeries.to_csv(path,"a")
        
        
class BitMex(WebsocketConnection):
    def __init__(self,ticker):
        
        self.ExchangeName = "BITMEX"
        self.ticker = ticker 
        self.webSocketURL ="wss://testnet.bitmex.com/realtime"
        self.instruments = ["XBTUSD"]
        self.location = "/Users/jeroenderyck/Documents/Data/CryptoPrices/"
        self.path = os.path.join(self.location, '%s_%s.csv' % (self.ExchangeName, self.ticker))
        
        
        if self.ValidateTicker(ticker):
          
            self.logger =setup_logger()

            self.ws = BitMEXWebsocket(endpoint="wss://testnet.bitmex.com/realtime", symbol= ticker,
                             api_key="wwvS30igJDo6Ksxa0h2EP1Eq", 
                             api_secret="-DOHRIUObpSQilqyr2y18YcTRi5NWFIV95du4i8rG4VveOBI")
            
            #self.logger.info("Instrument data: {}".format(self.ws.get_instrument()))


        else :
              print("please take an instrument available from bitmex", str(self.instruments))
        
    def streamPrices(self):
        source = ColumnDataSource(data=dict(timestamp=[], price=[]))

        while(self.ws.ws.sock.connected):
            
                timestamp, price = self.ws.GetPriceTimestamp()
                new_data = {
                                'timestamp' : timestamp,
                                'price' : price,
                            }
                source.stream(new_data)

                print("timestamp:", timestamp, "price", price)
                
                if os.path.exists(self.path):
                    print(" exists")
                    with open(self.path, 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([timestamp,price])

                else : 
                    print("does not exist")
                    with open(self.path, 'w') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames = ["timestamp","price"])
                        writer.writeheader()
                    
                time.sleep(1)

            

    def closeWebsocket(self):
        "Closing Websocket"
        self.ws.close()
        
    def ValidateTicker(self,ticker):
        return ticker in self.instruments
    
    
    
        
    
        
class GDAX(WebsocketConnection):
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

class CryptoCompare(object):
    
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
    
    
    
    
    
    
    