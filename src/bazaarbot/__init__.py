from bazaarbot._base import ISignalBankrupt
from random import Random


class MoneyItems(object):
    MONEY_AVAILABLE = "MONEY_AVAILABLE"
    MONEY = "MONEY"
    

class BazaarBotStaticImports(object):
    RANDOM_FACTORY = Random


class Economy(ISignalBankrupt):
    
    def __init__(self):
        self._markets = []
        
    def add_market(self, market):
        if market not in self._markets:
            self._markets.append(market)
    
    def get_market(self, name):
        for market in self._markets:
            if market.get_name() == name:
                return market
        return None
    
    def simulate(self, n_rounds):
        for market in self._markets:
            market.simulate(n_rounds)
    
    def signal_bankrupt(self, agent, market):
        pass
    

class Tradebook(object):
    
    def __init__(self):
        self._bids = {}
        self._asks = {}
        
    def register(self, commodity):
        self._bids[commodity] = []
        self._asks[commodity] = []
        
    def bid(self, offer):
        if offer.get_good() not in self._bids:
            self.register(offer.get_good())
        
        self._bids[offer.get_good()].append(offer)
    
    def ask(self, offer):
        if offer.get_good() not in self._bids:
            self.register(offer.get_good())
        
        self._asks[offer.get_good()].append(offer)
        
    def get_bids(self):
        return self._bids
    
    def get_asks(self):
        return self._asks
