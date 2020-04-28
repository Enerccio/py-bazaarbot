from builtins import range


class EcoNoun(object):
    
    PRICE = "PRICE"
    ASK = "ASK"
    BID = "BID"
    TRADE = "TRADE"
    PROFIT = "PROFIT"
    

class HistoryLog(object):
    
    def __init__(self, t=None, source=None):
        if type is None and source is None:
            raise TypeError("needs type or source")
        
        if type is not None:
            self._type = t
            self._log = {}
            
        if source is not None:
            self._type = source._type
            self._log = {}
            
            for key in source._log:
                self._log[key] = source._log[key] + []
                
    def add(self, name, amount):
        if name in self._log:
            self._log[name].append(amount)
            
    def register(self, name):
        if name not in self._log:
            self._log[name] = []
            
    def average(self, name, r):
        if name in self._log:
            l = self._log[name]
            amount = 0.0
            length = len(l)
            
            if length < r:
                r = length
                
            for i in range(r):
                amount += l[length - 1 - i]
                
            if r <= 0:
                return -1.0
            
            return amount / r
        return 0.0
    
    def get_subjects(self):
        return list(self._log.items())
    

class History(object):

    def __init__(self, src=None):
        self._prices = HistoryLog(EcoNoun.PRICE)
        self._asks = HistoryLog(EcoNoun.ASK)
        self._bids = HistoryLog(EcoNoun.BID)
        self._trades = HistoryLog(EcoNoun.TRADE)
        self._profit = HistoryLog(EcoNoun.PROFIT)
        
        if src is not None:
            self._prices = HistoryLog(src._prices)
            self._asks = HistoryLog(src._asks)
            self._bids = HistoryLog(src._bids)
            self._trades = HistoryLog(src._trades)
            self._profit = HistoryLog(src._profit)
            
    def register_commodity(self, good):
        self._prices.register(good)
        self._asks.register(good)
        self._bids.register(good)
        self._trades.register(good)
        self._profit.register(good)
        
    def get_commodities(self):
        result = set()
        
        for history_item in [self._prices, self._asks, self._bids, self._trades, self._profit]:
            result.add(history_item.get_subjects())
            
        return list(history_item)
    
    def get_prices(self):
        return self._prices
    
    def get_asks(self):
        return self._asks
    
    def get_bids(self):
        return self._bids
    
    def get_trades(self):
        return self._trades
    
    def get_profit(self):
        return self._profit
