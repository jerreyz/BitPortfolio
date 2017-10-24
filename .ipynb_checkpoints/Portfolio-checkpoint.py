import pandas as pd

class Portfolio(object):
    def __init__(self):
        raise NotImplementedError


class ProductPortfolio(Portfolio):
    
    def __init__(self,*args):
        self.prices = []
        self.products = []
        for product in (args):
            self.prices.append(product.DataframePresentation())
            self.products.append(product)
    def show(self):
        return pd.concat(self.prices,axis=1).resample("6T").first()
    def __str__(self): 
        result =[]
        for product in self.products:
            result.append(product.DataframePresentation())
        return str(pd.concat(result,axis=1).resample("6T").first())
            
        return str(pd.concat(self.prices,axis=1).resample("6T").first())
    def UpdatePrices(self):
        for i in self.products :
            i.UpdatePrice()