
try:
    import websocket
except ImportError:
    print("problem with websocket ")
from pprint import pprint
from json import dumps, loads
import logging
import sys


class GDAXWebsocket(object):
    def __init__(self,symbol):
        self.symbol =symbol
        self.URL    ="wss://ws-feed.gdax.com"
        self.logger = self.__setup_logger()
        self.__reset()
        self.ws = websocket.WebSocketApp(self.URL, 
                          on_open =self.__on_open, 
                          on_error = self.__on_error,
                          on_message=self.__on_message,
                          on_close=self.__on_close)
        
        
    def __on_close(self, ws):
        print("opened")
        #self.logger.info('Websocket Closed')
     
    def __setup_logger(self):
        # Prints logger info to terminal
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
        channel = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to ch
        channel.setFormatter(formatter)
        logger.addHandler(channel)
        return logger   
    
    
    def __on_message(self,_, message):
        """Callback executed when a message comes.

        Positional argument:
        message -- The message itself (string)
        """
        JSONmessage =(loads(message))
        self.message =JSONmessage
        pprint(self.message)
        
    def __on_error(self,ws, error):
         if not self.exited:
            self.logger.error("Error : %s" % error)
            sys.exit(1)

    def __on_open(self, ws):
        '''Called when the WS opens.'''
        self.logger.info("Websocket Opened.")
        self.logger.debug("Websocket Opened.")

        """Callback executed at socket opening.

        Keyword argument:
        socket -- The websocket itself
        """

        params = {
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": [self.symbol]}]
    }
        ws.send(dumps(params))

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.ws.close() 
        
    def __reset(self):
        '''Resets internal datastores.'''
        self.data = {}
        self.keys = {}
        self.exited = False
        
    def StreamMessage(self):

        self.ws.run_forever()
            
        
        
if __name__ == "__main__":
    test = GDAXWebsocket("BTC-USD")
    test.StreamMessage()