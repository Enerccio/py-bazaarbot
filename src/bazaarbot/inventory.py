from builtins import range


class InventoryData(object):
    def __init__(self, max_size, ideal, start):
        self._max_size = max_size
        self._ideal = ideal
        self._start = start
        
    def get_max_size(self):
        return self._max_size
    
    def set_max_size(self, max_size):
        self._max_size = max_size
        
    def get_ideal(self):
        return self._ideal
    
    def set_ideal(self, ideal):
        self._ideal = ideal
        
    def get_start(self):
        return self._start
    
    def set_start(self, start):
        self._start = start


class Inventory(object):
    
    class InventoryEntry(object):
        
        def __init__(self, amount, original_price):
            self._amount = amount
            self._original_price = original_price
            
        def get_amount(self):
            return self._amount
        
        def get_original_price(self):
            return self._original_price
        
    
    def __init__(self, other_inventory=None):
        self._stuff = {}
        self._ideal = {}
        self._expecting = {}
        self._max_size = 0
        
        if other_inventory is not None:
            self._stuff = other_inventory._stuff.copy()
            self._ideal = other_inventory._ideal.copy()
            self._expecting = other_inventory._expecting.copy()
            self._max_size = other_inventory._max_size.copy()
            
    def from_data(self, data):
        sizes = []
        amountsp = []
        
        for key in data.get_start():
            sizes.append(key)
            amountsp.append(Inventory.InventoryEntry(data.get_start()[key]), 0)
        
        for i in range(len(sizes)):
            self._stuff[sizes[i]] = amountsp[i]
        
        sizes = []
        amounts = []
        
        for key in data.get_ideal():
            sizes.append(key)
            amounts.add(data.get_ideal()[key])
            
        for i in range(len(sizes)):
            self._ideal[sizes[i]] = amounts[i]
        
        self._max_size = data.get_max_size()
    
    def query_amount(self, good):
        if good in self._stuff:
            return self._stuff[good].get_amount()
        
        return 0.0
    
    def query_expecting(self, good):
        if good in self._expecting:
            return self._expecting[good].get_amount()
        
        return 0.0
    
    def query_cost(self, good):
        if good in self._expecting:
            return self._expecting[good].get_original_price()
        
        return 0.0
    
    def get_empty_space(self):
        return self._max_size - self.get_used_space()
    
    def get_used_space(self):
        space_used = 0.0
        
        for key in self._stuff:
            space_used += self._stuff[key].get_amount() * key.get_space()
        
        return space_used
    
    def add(self, good, amount, unit_cost):
        if amount < 0 or good is None:
            return
        
        self._stuff[good] = Inventory.InventoryEntry(amount, unit_cost)
    
    def change(self, good, amount, unit_cost):
        if good not in self._stuff:
            return 0.0
        
        result_amount = 0.0
        result_price = 0.0
        
        current = self._stuff[good]
        
        if unit_cost > 0:
            if current.get_amount() <= 0:
                result_amount = amount
                result_price = unit_cost
            else:
                result_amount = current.get_amount() + amount
                result_price = (current.get_amount() * current.get_original_price() + amount * unit_cost) / (current.get_amount() + amount)
        else:
            result_amount = current.get_amount() + amount
            result_price = current.get_original_price()
            
        self._stuff[good] = Inventory.InventoryEntry(result_amount, result_price)
        return result_price
    
    def change_expecting(self, good, delta, unit_cost):
        result_amount = 0.0
        result_price = 0.0
        
        if good in self._expecting:
            current = self._expecting[good]
            
            if unit_cost > 0:
                if current.get_amount() <= 0:
                    result_amount = delta
                    result_price = unit_cost
                else:
                    result_amount = current.get_amount() + delta
                    result_price = (current.get_amount() * current.get_original_price() + delta * unit_cost) / (current.get_amount() + delta)
            else:
                result_amount = current.get_amount() + delta
                result_price = current.get_original_price()
        else:
            result_amount = delta
            result_price = unit_cost
        
        if result_amount < 0:
            result_amount = 0.0
            result_price = 0.0
            
        self._expecting[good] = Inventory.InventoryEntry(result_amount, result_price)
        return result_price
        
    def surplus(self, good):
        amount = self.query_amount(good)
        ideal = 0.0
        
        if good in self._ideal:
            ideal = self._ideal[good]
        
        if amount > ideal:
            return amount - ideal
        
        return 0.0
    
    def shortage(self, good):
        if good not in self._stuff:
            return 0.0
        
        amount = self.query_amount(good) + self.query_expecting(good)
        ideal = 0.0
        
        if good in self._ideal:
            ideal = self._ideal[good]
            
        if amount < ideal:
            return ideal - amount
        
        return 0.0
        
        
        
        
    
    
        
            