
class Exchange(object):
    def __init(self):
        return
    def GetPrice(self,symbol):
        raise NotImplementedError
        
class GDAX(Exchange):
    
    def GDAXstr(self,CurrencyPair):
        return CurrencyPair.baseCurrency+"-"+CurrencyPair.quoteCurrency
    def __str__(self):
        return "GDAX"

        
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
    def GetPrice(self,CurrencyPair):
        urlg ="https://min-api.cryptocompare.com/data/price?fsym="+CurrencyPair.baseCurrency+"&tsyms="+CurrencyPair.quoteCurrency
        decodedata = scrapeurl(urlg)
        return decodedata[CurrencyPair.quoteCurrency]