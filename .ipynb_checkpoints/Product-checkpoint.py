import os
import pandas as pd

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



class Product(object):
    def __init__(self, **args):
        raise NotImplementedError
        
class FXSpot(Product):
    
    def __init__(self, Exchange,CurrencyPair):
        self.Exchange     = Exchange
        self.ExchangeName = Exchange.__str__()
        self.CurrencyPair = CurrencyPair
        self.ticker       = CurrencyPair.__str__()
        self.TimeSeries   = pd.DataFrame(columns=["Price"+self.CurrencyPair.__str__()])
        self.SetPrice()
        
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
        
        
        
        
        
        