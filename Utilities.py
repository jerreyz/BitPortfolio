from urllib.request import urlopen
import json

def scrapeurl(url):
    page = urlopen(url)
    data = page.read()
    decodedata = json.loads(data.decode())
    return decodedata    

def getInstrument(symbol):
    return scrapeurl("https://www.bitmex.com/api/v1/instrument?symbol="+symbol)[0]

def pluck(dict, *args):
    '''Returns destructurable keys from dict'''
    return (dict[arg] for arg in args)

def valueBookLevel(multiplier, price, qty):
    '''Returns the value of a book level, in satoshis'''
    contVal = abs(multiplier * price if multiplier > 0 else multiplier / price)
    return round(qty * contVal)

def calculateImpactSide(instrument, book, side,DEBUG =False):
    '''
    The way we compute Impact Prices is by going into either side
    of the book for 10 BTC worth of order values, and take the average
    price filled.
    '''
    notional = 0
    impactPrice = 0

    for orderBookItem in book:
        size = orderBookItem[side + 'Size']
        price = orderBookItem[side + 'Price']

        # No more book levels; will create a situation where `hasLiquidity: false`
        if size is None or price is None:
            break

        # No more to do
        if notional >= IMPACT_NOTIONAL:
            break

        # Calculate value. Contract may be inverse, linear, or quanto.
        levelValue = valueBookLevel(instrument['multiplier'], price, size)

        # Calculate an average price, up to the IMPACT_NOTIONAL.
        remainingValue = min(levelValue, IMPACT_NOTIONAL - notional)
        notional += remainingValue
        impactPrice += (remainingValue / IMPACT_NOTIONAL) * price
        if DEBUG:
            print('side: %s, levelValue: %.2f, price: %.2f, size: %d, remainingValue: %.2f, notional: %.2f, impactPrice: %.2f' %
                  (side, levelValue / 1e8, price, size, remainingValue / 1e8, notional / 1e8, impactPrice))

    return impactPrice



def getImpactPrices(instrument):
    # Grab the Orderbook so we can grab the depth for bids and asks for impact prices
    symbol = instrument['symbol']
    fullBook = scrapeurl("https://www.bitmex.com/api/v1/orderBook?symbol="+symbol+"&depth=200")

    impactBid = calculateImpactSide(instrument, fullBook, 'bid')
    impactAsk = calculateImpactSide(instrument, fullBook, 'ask')

    # The % Fair Basis is updated each minute but only if the difference between the Impact Ask Price and
    # Impact Bid Price is less than the maintenance margin of the futures contract.
    # After it has been updated the Fair Price will be equal to the Impact Mid Price,
    # and then the Fair Price will float with regard to the Index Price and the time-to-expiry
    # decay on the contract until the next update.
    if abs(impactBid - impactAsk) > (instrument['midPrice'] / instrument['maintMargin']):
        print('Note: impactBid and impactAsk are farther apart than 1x maintMargin; hasLiquidity would be ' +
              'false, and the instrument\'s fair basis will not update until the prices converge again.')

    impactMid = (impactBid + impactAsk) / 2
    return (impactBid, impactMid, impactAsk)