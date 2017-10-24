from Portfolio import *
from Product import *
from Exchange import *
from  Utilities import *
from Currency import * 
from urllib.request import urlopen
import json
import dateutil.parser
import numpy as np

if __name__ =='__main__':
    Prices = ProductPortfolio(FXSpot(GDAX(),CurrencyPair("BTC","EUR")),
     FXSpot(GDAX(),CurrencyPair("ETH","EUR")),
     FXSpot(CryptoCompare(),CurrencyPair("IOT","ETH")))

    while True:
        Prices.UpdatePrices()
        print(Prices)
        time.sleep(180)