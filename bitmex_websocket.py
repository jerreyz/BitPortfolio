import sys
import websocket
import threading
import traceback
import time
from time import sleep
import json
import string
import logging
import os
import pandas as pd
import ssl 
import pprint

try:
    from urllib.parse import urlparse,urlunparse
except ImportError:
    from urlparse import urlparse,urlunparse

import math
from util.actual_kwargs import actual_kwargs
from util.api_key import generate_nonce, generate_signature
import Settings



# Naive implementation of connecting to BitMEX websocket for streaming realtime data.
# The Marketmaker still interacts with this as if it were a REST Endpoint, but now it can get
# much more realtime data without polling the hell out of the API.
#
# The Websocket offers a bunch of data as raw properties right on the object.
# On connect, it synchronously asks for a push of all this data then returns.
# Right after, the MM can start using its data. It will be updated in realtime, so the MM can
# poll really often if it wants.
class BitMEXWebsocket():

    # Don't grow a table larger than this amount. Helps cap memory usage.
    MAX_TABLE_LEN = 200

    # We use the actual_kwargs decorator to get all kwargs sent to this method so we can easily pass
    # it to a validator function.
    
    @actual_kwargs()
    def __init__(self,symbol=None, endpoint =Settings.BITMEX_ENDPOINT,api_key = Settings.API_KEY_BITMEX, api_secret =Settings.API_SECRET_BITMEX):
        '''Connect to the websocket and initialize data stores.'''
        #TODO change hardcoded instruments
        
        self.TradeableInstruments =["XBTUSD"]
        self.ExchangeName = "BitMEX"
        assert symbol in self.TradeableInstruments ,"Please pick an instrument from: "+ str(self.TradeableInstruments)
        
        self.logger = self.__setup_logger()
        self.logger.debug("Initializing WebSocket.")
        self.name = "BitMEX"

        self.__validate(self.__init__.actual_kwargs)
        self.__reset()
        self.config = {"symbol":symbol,"endpoint":endpoint,"api_key":api_key,"api_secret":api_secret}

       
        
        
        
    def connect(self, endpoint, symbol, shouldAuth=True):
        '''Connect to the websocket and initialize data stores.'''
        # Connect to websocket in websocket class
        self.logger.debug("Connecting WebSocket.")
        # Boolean
        self.shouldAuth = shouldAuth

        # We can subscribe right in the connection querystring, so let's build that.
        # Subscribe to all pertinent endpoints
        
        subscriptions = [sub + ':' + symbol for sub in ["quote", "trade"]]
        subscriptions += ["instrument"]  # We want all of them
        if self.shouldAuth:
            subscriptions += [sub + ':' + symbol for sub in ["order", "execution"]]
            subscriptions += ["margin", "position"]
        print("subscriptions:", subscriptions)
        print(self.config)
        # Get WS URL and connect.
        urlParts = list(urlparse(endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe=" + ",".join(subscriptions)
        wsURL = urlunparse(urlParts)
        self.logger.debug("Connecting to %s" % wsURL)
        self.__connect(wsURL)
        self.logger.debug('Connected to WS. Waiting for data images, this may take a moment...')

        # Connected. Wait for partials
        self.__wait_for_symbol(symbol)
        if self.shouldAuth:
            self.__wait_for_account()
        self.logger.info('Got all market data and account data. Starting.')
        
        
    ######### Private Method ##########     
    def __connect(self, wsURL):
        '''Connect to the websocket in a thread.'''
        self.logger.info("Starting thread")
        # Return paths to default cafile and capath.
        ssl_defaults = ssl.get_default_verify_paths()
        # dictionary holding defaults cafile = '/Users/jeroenderyck/anaconda/ssl/cert.pem'
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth()
                                         )

        self.__setup_logger()
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(sslopt=sslopt_ca_certs))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout and not self._error:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout or self._error:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            sys.exit(1)   
            
    def __reset(self):
    # Keep track of datastores
    # keep track of errors
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None    
        
        
        
    def __setup_logger(self):
        # log level can be (DEBUG|INFO|WARN|ERROR)
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        return logger
    
        
    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.ws.close()

    def get_instrument(self):
        '''Get the raw instrument data for this symbol.'''
        # Turn the 'tickSize' into 'tickLog' for use in rounding
        instrument = self.data['instrument'][0]
        instrument['tickLog'] = int(math.fabs(math.log10(instrument['tickSize'])))
        return instrument

    def get_ticker(self):
        '''Return a ticker object. Generated from quote and trade.'''
        lastQuote = self.data['quote'][-1]
        lastTrade = self.data['trade'][-1]
        ticker = {
            "last": lastTrade['price'],
            "buy": lastQuote['bidPrice'],
            "sell": lastQuote['askPrice'],
            "mid": (float(lastQuote['bidPrice'] or 0) + float(lastQuote['askPrice'] or 0)) / 2
        }

        # The instrument has a tickSize. Use it to round values.
        instrument = self.data['instrument'][0]
        # Python 3 uses items
        return ticker
    
    def GetPriceTimestamp(self):
        '''Return a ticker object. Generated from quote and trade.'''
        lastQuote = self.data['quote'][-1]
        lastTrade = self.data['trade'][-1]
        ticker = {
            "last": lastTrade['price'],
            "buy": lastQuote['bidPrice'],
            "sell": lastQuote['askPrice'],
            "mid": (float(lastQuote['bidPrice'] or 0) + float(lastQuote['askPrice'] or 0)) / 2
        }
        timestamp  =  pd.to_datetime(time.time(),unit="s")
        # The instrument has a tickSize. Use it to round values.
        instrument = self.data['instrument'][0]
        symbol = instrument["symbol"]
        return  timestamp, ticker["mid"]
    
    def getData(self):
        return self.data
    
    def error(self, err):
        self._error = err
        self.logger.error(err)
        self.exit()

    def funds(self):
        '''Get your margin details.'''
        return self.data['margin'][0]

    def market_depth(self):
        '''Get market depth (orderbook). Returns up to 25 levels.'''
        return self.data['orderBook25']

    def open_orders(self, clOrdIDPrefix):
        '''Get all your open orders.'''
        orders = self.data['order']
        # Filter to only open orders (leavesQty > 0) and those that we actually placed
        return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and o['leavesQty'] > 0]

    def recent_trades(self):
        '''Get recent trades.'''
        return self.data['trade']

    #
    # End Public Methods
    #

 

    def __get_auth(self):
        '''Return auth headers. Will use API Keys if present in settings.'''
        if self.config['api_key']:
            self.logger.info("Authenticating with API Key.")
            # To auth to the WS using an API key, we generate a signature of a nonce and
            # the WS API endpoint.
                # Create a number we use once 
            nonce = generate_nonce()
            #debugging
            #print(generate_signature(self.config['api_secret'], 'GET', '/realtime', nonce, ''))
            return [
                "api-nonce: " + str(nonce),
                "api-signature: " + generate_signature(self.config['api_secret'], 'GET', '/realtime', nonce, ''),
                "api-key:" + self.config['api_key']
            ]
        else:
            self.logger.info("Not authenticating.")
            return []
        
  
    
    def __get_url(self):
        '''
        Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.
        '''

        # You can sub to orderBook25 for top 25 levels, or orderBook10 for top 10 levels & save bandwidth
        symbolSubs = ["execution", "instrument", "order", "orderBook25", "position", "quote", "trade"]
        genericSubs = ["margin"]
        subscriptions = [sub + ':' + self.config['symbol'] for sub in symbolSubs]
        subscriptions += genericSubs
        urlParts = list(urlparse(self.config['endpoint']))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] =  os.path.join("/realtime?subscribe=",','.join(map(str, subscriptions)))
        return urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        # Wait for the keys to show up from the ws
        while not {'margin', 'position', 'order', 'orderBook25'} <= set(self.data):
            sleep(0.1)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {'instrument', 'trade', 'quote'} <= set(self.data):
            sleep(0.1)

    def __send_command(self, command, args=[]):
        '''Send a raw command.'''
        self.ws.send(json.dumps({"op": command, "args": args}))

    def __on_message(self, ws, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        self.logger.debug(json.dumps(message))

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        try:
            if 'subscribe' in message:
                self.logger.debug("Subscribed to %s." % message['subscribe'])
            elif action:

                if table not in self.data:
                    self.data[table] = []

                # There are four possible actions from the WS:
                # 'partial' - full table image
                # 'insert'  - new row
                # 'update'  - update row
                # 'delete'  - delete row
                if action == 'partial':
                    self.logger.debug("%s: partial" % table)
                    self.data[table] += message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self.keys[table] = message['keys']
                elif action == 'insert':
                    self.logger.debug('%s: inserting %s' % (table, message['data']))
                    self.data[table] += message['data']

                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if len(self.data[table]) > BitMEXWebsocket.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][(BitMEXWebsocket.MAX_TABLE_LEN / 2):]

                elif action == 'update':
                    self.logger.debug('%s: updating %s' % (table, message['data']))
                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = findItemByKeys(self.keys[table], self.data[table], updateData)
                        if not item:
                            return  # No item found to update. Could happen before push
                        item.update(updateData)
                        # Remove cancelled / filled orders
                        if table == 'order' and item['leavesQty'] <= 0:
                            self.data[table].remove(item)
                elif action == 'delete':
                    self.logger.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = findItemByKeys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown action: %s" % action)
        except:
            self.logger.error(traceback.format_exc())

   
    def __on_error(self, ws, error):
        if not self.exited:
            self.error(error)
            
    def __on_open(self, ws):
        '''Called when the WS opens.'''
        self.logger.debug("Websocket Opened.")

    def __on_close(self, ws):
        '''Called on websocket close.'''
        self.logger.info('Websocket Closed')
        sys.exit(1)

    def __validate(self, kwargs):
        '''Simple method that ensure the user sent the right args to the method.'''
        if 'symbol' not in kwargs:
            self.logger.error("A symbol must be provided explicitly to BitMEXWebsocket() Symbol = ...")
            sys.exit(1)
         #NOT USING THIS   
            """
        if 'endpoint' not in kwargs:
            self.logger.error("An endpoint (BitMEX URL) must be provided to BitMEXWebsocket()")
            sys.exit(1)
        if 'api_key' not in kwargs:
            self.logger.error("No authentication provided! Unable to connect.")
            sys.exit(1)
            """



# Utility method for finding an item in the store.
# When an update comes through on the websocket, we need to figure out which item in the array it is
# in order to match that item.
#
# Helpfully, on a data push (or on an HTTP hit to /api/v1/schema), we have a "keys" array. These are the
# fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through all
# provided keys.
def findItemByKeys(keys, table, matchData):
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item
