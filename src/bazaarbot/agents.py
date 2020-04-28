from bazaarbot.agent import IAgent, CommodityPricingHistory, AgentSnapshot
from bazaarbot.inventory import Inventory
from bazaarbot.market import Offer
from bazaarbot import MoneyItems, BazaarBotStaticImports


class DefaultAgent(IAgent):
    
    ASK_PRICE_INFLATION = 1.02
    DEFAULT_LOOKBACK = 15
    OBSERVE_WINDOW = 10;
    
    def __init__(self, agent_name, agent_simulation, inventory_data, money_available):
        self._agent_name = agent_name
        self._money_available = money_available
        self._inventory = Inventory()
        self._inventory.from_data(inventory_data)
        self._agent_simulation = agent_simulation
        self._money_spent = 0.0
        self._commodity_pricing_histories = []
        self._money_last_simulation = 0.0
        
    def determine_sale_quantity(self, observe_window, average_historical_price, commodity):
        if average_historical_price <= 0:
            return 0.0
        
        trading_range = self.observe_trading_range(commodity, observe_window)
        favorability = trading_range.position_in_range(average_historical_price) if trading_range is not None else 1.0
        
        amount_to_sell = round(favorability * self._inventory.surplus(commodity))
        
        if amount_to_sell < 1:
            amount_to_sell = 1.0
            
        return amount_to_sell
    
    def determine_purchase_quantity(self, observe_window, average_historical_price, commodity):
        if average_historical_price <= 0:
            return 0.0
        
        trading_range = self.observe_trading_range(commodity, observe_window)
        favorability = trading_range.position_in_range(average_historical_price) if trading_range is not None else 1.0
        
        amount_to_buy = round(favorability * self._inventory.shortage(commodity))
        
        if amount_to_buy < 1:
            amount_to_buy = 1.0
            
        return amount_to_buy
    
    def observe_trading_range(self, commodity, window):
        for cph in self._commodity_pricing_histories:
            if cph.get_commodity() == commodity:
                return cph.observe(window)
            
        return None
    
    def simulate(self, market):
        self._money_last_simulation = self._money_available
        self._agent_simulation.perform(self, market)
        
    def create_bid(self, market, commodity, limit):
        ideal = self.determine_purchase_quantity(DefaultAgent.OBSERVE_WINDOW,
                                                 market.get_average_historical_price(commodity, DefaultAgent.DEFAULT_LOOKBACK), commodity)
        
        quantity_to_buy = ideal if ideal > limit else limit
        bid_price = self._inventory.query_cost(commodity) * DefaultAgent.ASK_PRICE_INFLATION
        
        if quantity_to_buy > 0:
            return Offer(self, commodity, quantity_to_buy, bid_price)
        return None
    
    def create_ask(self, market, commodity, limit):
        ideal = self.determine_sale_quantity(DefaultAgent.OBSERVE_WINDOW,
                                                 market.get_average_historical_price(commodity, DefaultAgent.DEFAULT_LOOKBACK), commodity)
        
        quantity_to_sell = ideal if ideal > limit else limit
        ask_price = self._inventory.query_cost(commodity) * DefaultAgent.ASK_PRICE_INFLATION
        
        if quantity_to_sell > 0:
            return Offer(self, commodity, quantity_to_sell, ask_price)
        return None
    
    def generate_offers(self, market, commodity):
        surplus = self._inventory.surplus(commodity)
        
        if surplus >= 1:
            offer = self.create_ask(market, commodity, 1)
            market.ask(offer)
        else:
            shortage = self._inventory.shortage(commodity)
            space = self._inventory.get_empty_space()
            
            if shortage > 0 and space > 0:
                offer = self.create_bid(market, commodity, shortage)
            else:
                offer = self.create_bid(market, commodity, space)
            
            market.bid(offer)
            
    def update_price_model(self, act, commodity, success, unit_price):
        if success:
            for cph in self._commodity_pricing_histories:
                if cph.get_commodity() == commodity:
                    cph.add_transaction(unit_price)
    
    def add_inventory_item(self, good, amount):
        self._commodity_pricing_histories.append(CommodityPricingHistory(good))
        self._inventory.add(good, amount, (self._money_spent if self._money_spent >= 1 else 1.0) / amount)
    
    def query_inventory(self, commodity):
        return self._inventory.query_amount(commodity)
    
    def produce_inventory(self, good, delta):
        if self._money_spent < 1:
            self._money_spent = 1.0
            
        self._inventory.change(good, delta, self._money_spent / delta)
        self._money_spent = 0.0
        
    def consume_inventory_item(self, commodity, amount):
        if commodity.get_name() == MoneyItems.MONEY_AVAILABLE:
            self._money_available += amount
            if amount < 0:
                self._money_spent += -amount
        else:
            price = self._inventory.change(commodity, amount, 0.0)
            if amount < 0:
                self._money_spent += (-amount) * price
    
    def change_inventory(self, commodity, amount, unit_cost):
        if commodity.get_name() == MoneyItems.MONEY:
            self._money_available += amount
        else:
            self._inventory.change(commodity, amount, unit_cost)
            
    def get_snapshot(self):
        return AgentSnapshot(self.get_agent_name(), self.get_money_available(), Inventory(self._inventory))
        
    def is_inventory_full(self):
        return self._inventory.get_empty_space() == 0
    
    def get_last_simulate_profit(self):
        return self.get_money_available() - self._money_last_simulation
    
    def get_money_available(self):
        return self._money_available
    
    def set_money_available(self, value):
        self._money_available = value
        
    def __str__(self):
        return self._agent_name
    
    def get_agent_name(self):
        return self._agent_name
        
    
class AgentSimulation(object):
    
    def __init__(self, name, rnd=None):
        if rnd is None:
            rnd = BazaarBotStaticImports.RANDOM_FACTORY()
            
        self._name = name
        self._rnd = rnd
        
    def perform(self, agent, market):
        raise NotImplementedError()
    
    def produce(self, agent, commodity, amount, chance=1.0):
        if chance >= 1.0 or self._rnd.random():
            agent.add_inventory_item(commodity, amount)
    
    def consume(self, agent, commodity, amount, chance=1.0):
        if chance >= 1.0 or self._rnd.random():
            agent.consume_inventory_item(commodity, -amount)
    
    def get_name(self):
        return self._name
    
    def is_idle(self, agent, market):
        money = agent.get_money_available()
        money -= 2
        if money < 0:
            money = 0.0
        agent.set_money_available(money)

"""
author: Nick Gritsenko 
"""


class AgentSimulator2(object):
    
    def __init__(self, agent, rnd=None):
        if rnd is None:
            rnd = BazaarBotStaticImports.RANDOM_FACTORY()
            
        self._agent = agent
        self._rnd = rnd
    
    def simulate_activity(self):
        raise NotImplementedError()
    
    def produce(self, commodity, amount, chance=1.0):
        if chance >= 1.0 or self._rnd.random():
            self._agent.add_inventory_item(commodity, amount)
    
    def consume(self, commodity, amount, chance=1.0):
        if chance >= 1.0 or self._rnd.random():
            self._agent.consume_inventory_item(commodity, -amount)
    
    def get_name(self):
        return self._agent.get_agent_name()
    
    """Example:
    
    
    class AgentSimulatorExample2(AgentSimulator2):
        
        class A1(ICommodity):
            
            def get_name(self):
                return "Test"
                
            def get_space(self):
                return 1.0
                
        
        def simulate_activity(self):
            self._agent.add_inventory_item(AgentSimulatorExample2.A1(), 2)
    """
    
