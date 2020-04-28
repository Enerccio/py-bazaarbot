
class IContract(object):
    
    def complete(self):
        raise NotImplemented
    
    def abandon(self):
        raise NotImplemented
    

class IContractResolver(object):
    
    def new_contract(self, provider, receiver, good, units, clearing_price):
        raise NotImplemented
    
    
    def get_quote(self, source, dest, space):
        raise NotImplemented
    

class ContractQuote(object):
    
    def __init__(self, cost, risk, delivery_time):
        self._cost = cost
        self._risk = risk
        self._delivery_time = delivery_time
        
    def get_cost(self):
        return self._cost
    
    def get_risk(self):
        return self._risk
    
    def get_delivery_time(self):
        return self._delivery_time
    

class ProvideContract(IContract):
    
    def __init__(self, receiver, sell_contract, goods):
        self._receiver = receiver
        self._sell_contract = sell_contract
        self._goods = goods
        
    def complete(self):
        pass
    
    def abandon(self):
        pass
    

class DefaultContractResolver(IContractResolver):
    
    def new_contract(self, provider, receiver, good, units, clearing_price):
        provider.change_inventory(good, -units, 0.0)
        receiver.change_inventory(good, units, clearing_price)
        
    def get_quote(self, source, dest, space):
        return ContractQuote(0.0, 0.0, 0.0)
