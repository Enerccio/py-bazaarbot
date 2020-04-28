from builtins import range, staticmethod
from bazaarbot import BazaarBotStaticImports, Tradebook
from bazaarbot.history import History
from bazaarbot.agent import IAgent


class MarketOperations(object):
    BUY = "BUY"
    SELL = "SELL"
    

class IOfferExecutor(object):
    
    def execute(self, bid, ask):
        raise NotImplemented
    
    def reject_bid(self, offer, unit_price):
        raise NotImplemented
    
    def reject_ask(self, offer, unit_price):
        raise NotImplemented


class IOfferResolver(object):
    
    def resolve(self, executor, bids, asks):
        raise NotImplemented
    
    
class DefaultOfferExecutor(IOfferExecutor):
    
    def execute(self, buyer, seller):
        quantity_traded = min(buyer.get_units(), seller.get_units())
        clearing_price = seller.get_unit_price()
        good = buyer.get_good()
        
        
        buyer_agent = buyer.get_agent()
        seller_agent = seller.get_agent()
        
        self.transfer_good(good, quantity_traded, seller_agent, buyer_agent, clearing_price)
        self.transfer_money(quantity_traded * clearing_price, seller_agent, buyer_agent)
        
        buyer_agent.update_price_model(MarketOperations.BUY, buyer.get_good(), True, clearing_price)
        seller_agent.update_price_model(MarketOperations.SELL, seller.get_good(), True, clearing_price)
        
    def reject_bid(self, buyer, unit_price):
        buyer.get_agent().update_price_model(MarketOperations.BUY, buyer.get_good(), False, unit_price)
       
    def reject_ask(self, seller, unit_price):
        seller.get_agent().update_price_model(MarketOperations.SELL, seller.get_good(), False, unit_price)

    def transfer_good(self, good, units, seller, buyer, clearing_price):
        seller.change_inventory(good, -units, 0.0)
        buyer.change_inventory(good, units, clearing_price)
        
    def transfer_money(self, amount, seller, buyer):
        seller.set_money_available(seller.get_money_available() + amount)
        buyer.set_money_available(buyer.get_money_available() - amount)


class Offer(object):
    
    def __init__(self, agent, commodity, units, unit_price):
        self._agent = agent
        self._commodity = commodity
        self._units = units
        self._unit_price = unit_price
        self._time_put = 0

    def get_agent(self):
        return self._agent

    def get_good(self):
        return self._commodity

    def get_units(self):
        return self._units

    def get_unit_price(self):
        return self._unit_price

    def set_agent(self, value):
        self._agent = value

    def set_good(self, value):
        self._commodity = value

    def set_units(self, value):
        self._units = value

    def set_unit_price(self, value):
        self._unit_price = value
    
    def get_time_put(self):
        return self._time_put
    
    def __str__(self):
        return "(" + str(self._agent) + "): " + str(self._commodity) + "x " + str(self._units) + "@ " + str(self._unit_price)
    
    
class OfferExecutionStatistics(object):
    
    def __init__(self, units_traded, money_traded):
        self._units_traded = units_traded
        self._money_traded = money_traded
    
    def get_units_traded(self):
        return self._units_traded
    
    def get_money_traded(self):
        return self._money_traded
    
    
class OfferResolutionStatistics(object):
    
    def __init__(self, resolved_offers):
        self._offers_resolved = len(resolved_offers)
        self._resolved_offers = resolved_offers
        
        units_traded = 0.0
        money_traded = 0.0
        
        for e in self._resolved_offers:
            units_traded += e.get_units_traded()
            money_traded += e.get_money_traded()
            
        self._units_traded = units_traded
        self._money_traded = money_traded
        
    def get_offers_resolved(self):
        return self._offers_resolved
    
    def get_money_traded(self):
        return self._money_traded
    
    def get_resolved_offers(self):
        return self._resolved_offers
    
    def get_units_traded(self):
        return self._units_traded
        

class DefaultOfferResolver(IOfferResolver):
    
    def __init__(self, rnd=None):
        if rnd is None:
            rnd = BazaarBotStaticImports.RANDOM_FACTORY()
            
        self._rng = rnd
        
    @staticmethod
    def sort_offers(offers):
        offers.sort(key=Offer.get_unit_price)
        
    def resolve(self, executor, bids, asks):
        result = {}
        
        for c in bids:
            if c not in asks:
                continue
            
            r = self.resolve_offer_set(executor, bids[c], asks[c])
            result[c] = r
        
        return result
    
    def resolve_offer_set(self, executor, bids, asks):
        self._rng.shuffle(bids)
        self._rng.shuffle(asks)
        
        DefaultOfferResolver.sort_offers(asks)
        
        resolved_offers = []
        
        while len(bids) > 0 and len(asks) > 0:
            buyer = bids[0]
            seller = asks[0]
            
            r = executor.execute(buyer, seller)
            
            if r.get_units_traded() > 0:
                resolved_offers.append(r)
                seller.set_units(seller.get_units() - r.get_units_traded())
                buyer.set_units(buyer.get_units() + r.get_units_traded())
            
            if seller.get_units() == 0:
                del asks[0]
            
            if buyer.get_units() == 0:
                del bids[0]
                
        for offer in bids:
            executor.reject_bid(offer, offer.get_unit_price())
        
        for offer in asks:
            executor.reject_ask(offer, offer.get_unit_price())
            
        return OfferResolutionStatistics(resolved_offers)
            

class MarketData(object):
    
    def __init__(self, goods, agents):
        self.goods = goods
        self.agents = agents
        

class MarketSnapshot(object):
    
    def __init__(self, history, agents):
        self._history = history
        self._agents = agents
        
    def get_history(self):
        return self._history
    
    def get_agents(self):
        return self._agents


class MarketInitConfig(object):
    
    def get_starting_trade(self, commodity, default=1.0):
        return default
    

class Market(object):
    
    def __init__(self, name, market_data, isb, offer_resolver, executor, market_init, rng=None):
        if rng is None:
            rng = BazaarBotStaticImports.RANDOM_FACTORY()
            
        self._name = name
        self._history = History()
        self._trade_book = Tradebook()
        self._good_types = []
        self._agents = []
        self._signal_bankrupt = isb
        self._offer_resolver = offer_resolver
        self._offer_executor = executor
        self._rng = rng
        self._round_num = 0
        
        self.from_data(market_data, market_init)
        
    def replace_agent(self, old_agent, new_agent):
        self._agents[self._agents.index(old_agent)] = new_agent
        
    def get_name(self):
        return self._name
    
    def simulate(self, rounds):
        
        for _ in range(rounds):
            for agent in self._agents:
                agent.simulate(self)
                
                for commodity in self._good_types:
                    agent.generate_offers(self, commodity)
            
            
            self.resolve_offers()
            
            todel = []
            
            for agent in self._agents:
                if agent.get_money_available() <= 0:
                    todel.append(agent)
            
            while len(todel) > 0:
                self._signal_bankrupt.signal_bankrupt(self, todel[0])
                del todel[0]

            self._round_num += 1

    def ask(self, offer):
        self._trade_book.ask(offer)
    
    def bid(self, offer):
        self._trade_book.bid(offer)
        
    def get_average_historical_price(self, good, r):
        return self._history.get_prices().average(good, r)
    
    def get_hottest_good(self, minimum=1.5, r=10):
        best_market = None
        best_ratio = -float("inf")
        
        for good in self._good_types:
            asks = self._history.get_asks().average(good, r)
            bids = self._history.get_bids().average(good, r)
            
            if asks == 0 and bids > 0:
                # If there are NONE on the market we artificially create a fake supply of 1/2 a unit to avoid the
                # crazy bias that "infinite" demand can cause...
                asks = 0.5
        
            ratio = bids / asks
            if ratio > minimum and ratio > best_ratio:
                best_ratio = ratio
                best_market = good
        
        return best_market
    
    def get_cheapest_good(self, r, exclude):
        best_price = float("inf")
        best_good = None
        
        for g in self._good_types:
            if exclude is None or g not in exclude:
                price = self._history.get_prices().average(g, r)
                if price < best_price:
                    best_price = price
                    best_good = g
        
        return best_good
        
    def get_dearest_good(self, r, exclude):
        best_price = -float("inf")
        best_good = None
        
        for g in self._good_types:
            if exclude is None or g not in exclude:
                price = self._history.get_prices().average(g, r)
                if price > best_price:
                    best_price = price
                    best_good = g
        
        return best_good
    
    def get_agent_class_names(self):
        classes = set()
        
        for agent in self._agents:
            classes.add(agent.get_agent_name())
            
        return list(classes)
    
    def get_most_profitable_agent(self, r=10):
        best = -float("inf")
        best_class = ""
        
        for class_name in self.get_agent_class_names():
            val = self._history.get_profit().average(class_name, r)
            if val > best:
                best_class = class_name
                best = val
        
        return best_class
    
    def get_snapshot(self):
        agent_data = []
        
        for a in self._agents:
            agent_data.append(a.get_snapshot())
        
        return MarketSnapshot(History(self._history), agent_data)
    
    def from_data(self, data, market_init):
        for g in data.goods:
            self._good_types.append(g)
            v = market_init.get_starting_trade(g, 1.0)
            
            self._history.register_commodity(g)
            self._history.get_prices().add(g, v)
            self._history.get_asks().add(g, v)
            self._history.get_bids().add(g, v)
            self._history.get_trades().add(g, v)
            
            self._trade_book.register(g)
        
        self._agents = []
        self._agents += data.agents
        
    @staticmethod
    def list_avg(l):
        avg = 0.0
        
        for v in l:
            avg += v
        
        avg /= len(l)
        return avg
    
    def resolve_offers(self):
        for key in self._trade_book.get_asks():
            offers = self._trade_book.get_asks()[key]
            count = 0.0
            
            for o in offers:
                count += o.get_units()
            
            self._history.get_asks().add(key, count)
        
        for key in self._trade_book.get_bids():
            offers = self._trade_book.get_bids()[key]
            count = 0.0
            
            for o in offers:
                count += o.get_units()
            
            self._history.get_bids().add(key, count)
            
        r = self._offer_resolver.resolve(self._offer_executor, self._trade_book.get_bids().copy(), self._trade_book.get_asks().copy())
        self._trade_book.get_asks().clear()
        self._trade_book.get_bids().clear()
        
        for key in r:
            stats = r[key]
            self._history.get_trades().add(key, stats.get_units_traded())
            
            if stats.get_units_traded() > 0:
                self._history.get_prices().add(key, stats.get_money_traded() / stats.get_units_traded())
            else:
                # special case: none were traded this round, use last round's average price
                self._history.get_prices().add(key, self._history.get_prices().average(key, 1))
        
        ag = [] + self._agents
        ag.sorted(key=IAgent.get_agent_name)
        
        curr_class = ""
        last_class = ""
        l = None
        
        for i in range(len(ag)):
            a = ag[i]
            curr_class = a.get_agent_name()
            
            if curr_class != last_class:
                if l is not None:
                    self._history.get_profit().add(last_class, Market.list_avg(l))
                
                l = []
                last_class = curr_class
            
            l.append(a.get_last_simulate_profit())
            
        if l is not None:
            self._history.get_profit().add(last_class, Market.list_avg(l))
