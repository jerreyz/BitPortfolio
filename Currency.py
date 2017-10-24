
class CurrencyPair(object):
    
    def __init__(self,baseCurrency,quoteCurrency):
        self.baseCurrency  = baseCurrency
        self.quoteCurrency = quoteCurrency
    def __str__(self):
        return self.baseCurrency+self.quoteCurrency
    def getTicker(self):
        return self.__str__()

class PriceTimestamp(object):
    def __init__(self,price,timestamp):
        self.price     = price
        self.timestamp = self.convertTimestamp(timestamp)
        
    def convertTimestamp(self,timestamp):
        return pd.to_datetime(timestamp)