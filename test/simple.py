from bazaarbot import Economy
import random
from bazaarbot.agent import IAgentFactory
from bazaarbot.agents import AgentSimulation, DefaultAgent
from bazaarbot._base import ICommodity, SimpleCommodity, ISignalBankrupt
from bazaarbot.inventory import InventoryData
from bazaarbot.market import MarketData, MarketInitConfig, Market,\
    DefaultOfferResolver, DefaultOfferExecutor

GOOD_crops = SimpleCommodity("crops", 1.0)
GOOD_wood = SimpleCommodity("wood", 2.0)


class FarmerAgentSimulator(AgentSimulation):
    
    def __init__(self, rng):
        AgentSimulation.__init__(self, "farmer", rng)
        
    def perform(self, agent, market):
        wood = agent.query_inventory(GOOD_wood)
        food = agent.query_inventory(GOOD_crops)
        
        need_food = food < 10
        has_wood = wood >= 1
        
        if need_food:
            if has_wood:
                self.consume(agent, GOOD_wood, 1)
                self.produce(agent, GOOD_crops, 6)
            else:
                self.is_idle(agent, market)   


class FarmerAgentFactory(IAgentFactory):
    
    def __init__(self, rng):
        self._rng = rng
    
    def create(self):
        ideal = {}
        start = {}
        
        ideal[GOOD_crops] = 0.0
        ideal[GOOD_wood] = 3.0
        start[GOOD_crops] = 1.0
        start[GOOD_wood] = 0.0
        
        inv = InventoryData(20, ideal, start)
        return DefaultAgent("Farmer", FarmerAgentSimulator(self._rng), inv, 100.0)
    
    
class WoodcutterAgentSimulator(AgentSimulation):
    
    def __init__(self, rng):
        AgentSimulation.__init__(self, "woodcutter", rng)
    
    def perform(self, agent, market):
        wood = agent.query_inventory(GOOD_wood)
        food = agent.query_inventory(GOOD_crops)
        
        need_wood = wood < 4
        has_food = food >= 1
        
        if need_wood:
            if has_food:
                self.consume(agent, GOOD_crops, 1)
                self.produce(agent, GOOD_wood, 4)
            else:
                self.is_idle(agent, market)   


class WoodcutterAgentFactory(IAgentFactory):
    
    def __init__(self, rng):
        self._rng = rng
    
    def create(self):
        ideal = {}
        start = {}
        
        ideal[GOOD_crops] = 3.0
        ideal[GOOD_wood] = 0.0
        start[GOOD_crops] = 0.0
        start[GOOD_wood] = 1.0
        
        inv = InventoryData(20, ideal, start)
        return DefaultAgent("Woodcutter", WoodcutterAgentSimulator(self._rng), inv, 100.0)
    

class SimpleEconomy(Economy):
    
    def __init__(self, rng=None):
        Economy.__init__(self)
        
        if rng is None:
            rng = random.Random()
            
        self.rng = rng
        self.farmer_factory = FarmerAgentFactory(rng)
        self.woodcutter_factory = WoodcutterAgentFactory(rng)
        
        market_data = self.get_market_data()
        market_init = MarketInitConfig()
        
        market = Market("market", market_data, self, DefaultOfferResolver(rng), 
                        DefaultOfferExecutor(), market_init, rng)
        self.add_market(market)
    
    def signal_bankrupt(self, agent, market):
        self.replace_agent(market, agent)
    
    def get_market_data(self):
        agents = []
        
        agents.append(self.farmer_factory.create())
        agents.append(self.farmer_factory.create())
        agents.append(self.farmer_factory.create())
        agents.append(self.farmer_factory.create())
        agents.append(self.farmer_factory.create())
        agents.append(self.woodcutter_factory.create())
        agents.append(self.woodcutter_factory.create())
        agents.append(self.woodcutter_factory.create())
        agents.append(self.woodcutter_factory.create())
        agents.append(self.woodcutter_factory.create())
        
        return MarketData([GOOD_crops, GOOD_wood], agents)
    
    def replace_agent(self, market, agent):
        best_class = market.get_most_profitable_agent()
        
        if best_class is None:
            best_class = "farmer"
            
        market.replace_agent(agent, self.instatiate_agent(best_class))
    
    def instatiate_agent(self, class_name):
        if "farmer" == class_name:
            return self.farmer_factory.create()
        if "woodcutter" == class_name:
            return self.woodcutter_factory.create()
        
        
if __name__ == "__main__":
    e = SimpleEconomy(rng = random.Random(1))
    e.simulate(100)
    