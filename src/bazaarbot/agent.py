from builtins import range
    
    
class IAgent(object):
    
    def simulate(self, market):
        raise NotImplemented
    
    def create_bid(self, market, commodity, limit):
        raise NotImplemented
    
    def create_ask(self, market, commodity, limit):
        raise NotImplemented
    
    def generate_offers(self, market, commodity):
        raise NotImplemented
    
    def update_price_model(self, act, commodity, success, unit_price):
        raise NotImplemented
    
    def add_inventory_item(self, good, amount):
        raise NotImplemented
    
    def query_inventory(self, commodity):
        raise NotImplemented
    
    def produce_inventory(self, good, delta):
        raise NotImplemented
    
    def consume_inventory_item(self, commodity, amount):
        raise NotImplemented
    
    def change_inventory(self, commodity, amount, unit_cost):
        raise NotImplemented
    
    def get_snapshot(self):
        raise NotImplemented
    
    def is_inventory_full(self):
        raise NotImplemented
    
    def get_last_simulate_profit(self):
        raise NotImplemented
    
    def get_agent_name(self):
        raise NotImplemented
    
    def get_money_available(self):
        raise NotImplemented
    
    def set_money_available(self, value):
        raise NotImplemented
    

class IAgentClass(object):
    
    def get_name(self):
        raise NotImplemented
    
    def get_factory(self):
        raise NotImplemented
    

class IAgentFactory(object):
    
    def create(self):
        raise NotImplemented
    
    
class CommodityPricingRange(object):
    
    def __init__(self, commodity, minv, maxv):
        self._commodity = commodity
        self._min = minv
        self._max = maxv
        
    def get_min(self):
        return self._min
    
    def get_max(self):
        return self._max
    
    def position_in_range(self, value, clamp=True):
        value -= self._min
        
        working_max = self._max - self._min
        working_min = 0.0
        
        value = (value / (working_max - working_min))
        
        if clamp:
            if value < 0:
                value = 0.0
            
            if value > 1:
                value = 1.0
                
        return value
    
    def get_commodity(self):
        return self._commodity
    

class CommodityPricingHistory(object):
    
    def __init__(self, commodity, *prices):
        self._commodity = commodity
        
        if len(prices) == 0:
            prices = (2.0, 6.0)
        
        self._observed = list(prices)
        
    def _limit(self, window):
        return len(self._observed) if window > len(self._observed) else window
        
    def min(self, window):
        window = self._limit(window)
        
        minv = None
        
        for i in range(window):
            minv = self._observed[i] if minv is None else min(minv, self._observed[i])
        
        return minv if minv is not None else 0.0 
    
    def max(self, window):
        window = self._limit(window)
        
        maxv = None
        
        for i in range(window):
            maxv = self._observed[i] if maxv is None else max(maxv, self._observed[i])
        
        return maxv if maxv is not None else 0.0 

    def observe(self, window):
        return CommodityPricingRange(self._commodity, self.min(window), self.max(window))
    
    def add_transaction(self, unit_price):
        self._observed.append(unit_price)
        
    def get_commodity(self):
        return self._commodity
    
    
class AgentSnapshot(object):
    
    def __init__(self, class_name, money, inv):
        self._money = money
        self._inventory = inv
        self._class_name = class_name
        
    def get_money(self):
        return self._money
    
    def get_class_name(self):
        return self._class_name
    
    def get_inventory(self):
        return self._inventory
    
    
    
    
    
    
    
    
    
    
    
    
    
    