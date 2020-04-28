
class ISignalBankrupt(object):
    
    def signal_bankrupt(self, agent, market):
        raise NotImplemented
    

class ICommodity(object):
    
    def get_name(self):
        raise NotImplemented
    
    def get_space(self):
        raise NotImplemented