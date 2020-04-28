

class ISignalBankrupt(object):
    
    def signal_bankrupt(self, agent, market):
        raise NotImplementedError()
    

class ICommodity(object):
    
    def get_name(self):
        raise NotImplementedError()
    
    def get_space(self):
        raise NotImplementedError()
    
    def __eq__(self, other):
        return self.get_name() == other.get_name()
    
    def __hash__(self):
        return hash(self.get_name())


class SimpleCommodity(ICommodity):
    
    def __init__(self, name, space):
        self._name = name
        self._space = space
        
    def get_name(self):
        return self._name
    
    def get_space(self):
        return self._space
    
    def __str__(self):
        return self.get_name()