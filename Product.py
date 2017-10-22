import os

class CurrencyPair(object):
    
    def __init__(self,baseCurrency,quoteCurrency):
        self.baseCurrency  = baseCurrency
        self.quoteCurrency = quoteCurrency
    def __str__(self):
        return self.baseCurrency+self.quoteCurrency

class PriceTimestamp(object):
    def __init__(self,price,timestamp):
        self.price     = price
        self.timestamp = self.convertTimestamp(timestamp)
        
    def convertTimestamp(self,timestamp):
        return pd.to_datetime(timestamp).round("1min")
    



class Product(object):
    def __init__(self, **args):
        raise NotImplementedError
        
class FXSpot(Product):
    
    def __init__(self, Exchange,CurrencyPair):
        self.Exchange     = Exchange
        self.ExchangeName = Exchange.__str__()
        self.CurrencyPair = CurrencyPair
        self.TimeSeries   = pd.DataFrame(columns=["Price"+self.CurrencyPair.__str__()])
        self.SetPrice()
        self.SaveTimeSeries()
        
    def __str__(self):
        return str(pd.DataFrame({"Price"+self.CurrencyPair.__str__():[self.priceTimestamp.price]},
                                index =[self.priceTimestamp.timestamp]))
        
    def SaveTimeSeries(self,location = "/Users/jeroenderyck/Documents/Data/CryptoPrices/"):
        path = os.path.join(location, '%s_%s.csv' % (self.ExchangeName, self.CurrencyPair.__str__()))
        self.TimeSeries.to_csv(path)
        
    def UpdateTimeSeries(self,location ="/Users/jeroenderyck/Documents/Data/CryptoPrices/"):
        with open(location+self.ExchangeName+ self.CurrencyPair.__str__(), 'a') as database:
            self.TimeSeries.to_csv(database, header=True)
            
    def SetPrice(self):
        self.priceTimestamp = self.Exchange.GetPriceTimestamp(self.CurrencyPair)
        self.TimeSeries.loc[ self.priceTimestamp.timestamp] = self.priceTimestamp.price
        
    def UpdatePrice(self):
        self.priceTimestamp = self.Exchange.GetPriceTimestamp(self.CurrencyPair)
        self.TimeSeries.loc[ self.priceTimestamp.timestamp] = self.priceTimestamp.price
        self.SaveTimeSeries()