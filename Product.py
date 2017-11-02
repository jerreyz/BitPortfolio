import os
import pandas as pd
#from util.TerminalDecorator import TerminalDecorator
from util.setup_logger import setup_logger
import csv
from time import sleep

class CurrencyPair(object):
    
    def __init__(self,baseCurrency,quoteCurrency):
        self.baseCurrency  = baseCurrency
        self.quoteCurrency = quoteCurrency
    def __str__(self):
        return self.baseCurrency+self.quoteCurrency
    
    def ticker(self):
        return self.__str__()

class PriceTimestamp(object):
    def __init__(self,price,timestamp):
        self.price     = price
        self.timestamp = self.convertTimestamp(timestamp)
        
    def convertTimestamp(self,timestamp):
        return pd.to_datetime(timestamp)



class Position(object):
    def __init__(self, **args):
        raise NotImplementedError
 


    
class FXSpotTrade(Position):
    
    def __init__(self, WebsocketConnection,CurrencyPair):
        # Method 1 initialize websocket at product level
        self.CurrencyPair = CurrencyPair
        self.ticker       = CurrencyPair.__str__()
        self.Websocket    = WebsocketConnection(symbol = self.ticker)
        
        if (self.Websocket.config[apiKey] is None):
            raise Exception("Please set an API key and Secret to get started. See ")
                         
        self.ExchangeName = self.Websocket.ExchangeName
        print(self.Websocket.ws.sock.connected)
        # set location
        self.location = "/Users/jeroenderyck/Documents/Data/CryptoPrices/"
        self.path = os.path.join(self.location, '%s_%s.csv' % (self.ExchangeName, self.ticker))
        
        self.logger =setup_logger()
        self.price =0
        self.timestamp =0
        print('{:^10}{:>15}'.format("timestamp","price"))
              

      
    def streamPrices(self):
        while  (self.Websocket.ws.sock.connected):
            timestamp, price = self.Websocket.GetPriceTimestamp()
            if price == self.price:
                pass
            else : 
                self.timestamp, self.price = self.Websocket.GetPriceTimestamp()
            #print ('>>%20{}<<').format(self.timestamp)
                print('{:{dfmt} {tfmt}}'.format(self.timestamp, dfmt='%Y-%m-%d', tfmt='%H:%M'),
                '{:10.4f}'.format( self.price))
                if os.path.exists(self.path):
                        with open(self.path, 'a') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([self.timestamp,self.price])

                else : 
                        with open(self.path, 'w') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames = ["timestamp","price"])
                            writer.writeheader()

                sleep(1)
       
            
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
        
        
    def DataframePresentation(self):
        return pd.DataFrame({"Price"+self.ticker:[self.priceTimestamp.price]},
                                index =[self.priceTimestamp.timestamp])
    
    def __str__(self):
        return str(pd.DataFrame({"Price"+self.ticker:[self.priceTimestamp.price]},
                                index =[self.priceTimestamp.timestamp]))
        
    def SaveTimeSeries(self,location = "/Users/jeroenderyck/Documents/Data/CryptoPrices/"):
        path = os.path.join(location, '%s_%s.csv' % (self.ExchangeName, self.ticker))
        self.TimeSeries.to_csv(path,"a")
        
    def GetPrice(self):
        return self.priceTimestamp.price
    
    def SetPrice(self):
        self.priceTimestamp = self.Exchange.GetPriceTimestamp(self.CurrencyPair)
        self.TimeSeries.loc[ self.priceTimestamp.timestamp] = self.priceTimestamp.price
        
    def UpdatePrice(self):
        self.priceTimestamp = self.Exchange.GetPriceTimestamp(self.CurrencyPair)
        self.TimeSeries.loc[ self.priceTimestamp.timestamp] = self.priceTimestamp.price
        self.SaveTimeSeries()
        
        
        
class test(object):
    
    def __init__(self,websocket):
        self.Websocket    = WebsocketConnection(symbol = "XBTUSD")
        
        