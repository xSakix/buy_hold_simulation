import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymc3 as pm


class DCA:
    def __init__(self, period=30, cash=300.):
        self.period = period
        self.cash = cash


class Investor:
    def __init__(self, dca=DCA()):
        self.cash = 0.
        self.invested = 0.
        self.shares = 0
        self.returns = 0.
        self.gains = 0.
        self.dca = dca


class BuyAndHoldInvestmentStrategy:
    def __init__(self, investor=Investor(), tr_cost=2.):
        self.investor = investor
        self.tr_cost = tr_cost

    def invest(self, data, ring=None, position=None):
        if len(data.keys()) == 0:
            return

        indexes = data.index[data.index % self.investor.dca.period == 0]
        if ring is not None and position is not None:
            index_selector = np.arange(len(indexes))
            indexes = indexes[index_selector % ring == position]

        prices = data.ix[indexes].values
        prices = prices.reshape(prices.shape[0], )
        invested = np.full((len(prices),), fill_value=self.investor.dca.cash)
        invest_minus_tr_cost = np.subtract(invested, 2.)
        shares = np.round(np.divide(invest_minus_tr_cost, prices))
        real_invest = np.multiply(shares, prices)
        cash = np.sum(np.subtract(invest_minus_tr_cost, real_invest))
        self.investor.shares = np.sum(shares)
        self.investor.invested = np.sum(invested)
        try:
            self.investor.gains = np.sum(shares) * data.iloc[-1].values[0] + cash
        except:
            self.investor.gains = np.sum(shares) * data.iloc[-1] + cash
        self.investor.returns = (self.investor.gains - self.investor.invested) / self.investor.invested


class SimpleBuyAndHoldMultiple:
    def __init__(self, tickets, tr_cost=2.):
        self.investor = Investor()
        self.strategies = []
        self.tickets = tickets
        for i in range(len(tickets)):
            investor = Investor(dca=DCA(period=30, cash=300.))
            self.strategies.append(BuyAndHoldInvestmentStrategy(investor, tr_cost))
        self.tr_cost = tr_cost

    def invest(self, data_sources):
        for i in range(len(self.tickets)):
            for data in data_sources:
                if self.tickets[i] in data.keys():
                    self.strategies[i].invest(data[[self.tickets[i]]].reindex(), ring=len(self.tickets), position=i)
                    self.investor.invested += self.strategies[i].investor.invested
                    self.investor.gains += self.strategies[i].investor.gains

        self.investor.returns = (self.investor.gains - self.investor.invested) / self.investor.invested
