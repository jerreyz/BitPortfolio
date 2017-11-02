from Portfolio import *
from Product import *
from  Utilities import *
from Currency import * 
from urllib.request import urlopen
import json
import dateutil.parser
import numpy as np
import json
import dateutil.parser
from prettytable import PrettyTable
import pandas as pd
import time
import numpy as np
import os
from bitmex_websocket import BitMEXWebsocket
from util.setup_logger import setup_logger
import Settings


if __name__ =='__main__':
        """

        ws = BitMEXWebsocket(endpoint="wss://testnet.bitmex.com/realtime", symbol="XBTUSD",
                                  api_key="wwvS30igJDo6Ksxa0h2EP1Eq", api_secret="-DOHRIUObpSQilqyr2y18YcTRi5NWFIV95du4i8rG4VveOBI")
        # accessing websocket from pip websocket
        while(ws.ws.sock.connected):
            logger.info("Ticker: %s" % ws.get_ticker())
            time.sleep(10)

        """
        
        # Create a new Product
        test = BitMEXWebsocket(symbol ="XBTUSD")
        test.connect(endpoint = Settings.BITMEX_ENDPOINT, symbol ="XBTUSD")
        
            
