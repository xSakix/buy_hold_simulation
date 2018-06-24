import numpy as np


class DCA:
    def __init__(self, period=30, cash=300.):
        self.period = period
        self.cash = cash


class Investor:
    def __init__(self, ticket, dist, dca=DCA()):
        self.ticket = ticket
        self.cash = 0.
        self.invested = 0.
        self.history = []
        self.invested_history = []
        self.ror_history = []
        self.shares = []
        self.dist = dist
        self.dca = dca

class BuyAndHoldInvestmentStrategy:
    def __init__(self, investor, tr_cost):
        self.investor = investor
        self.tr_cost = tr_cost

    def invest(self, data, tickets=None):

        if len(data.keys()) == 0:
            return
        if tickets is None:
            tickets = data.keys()

        self.investor.shares = np.zeros(len(tickets))

        day = 0

        for i in data.index:
            try:
                prices = data.loc[i].values
            except:
                prices = data.loc[i]

            if (prices == 0.).any():
                continue
            portfolio = self.investor.cash + np.dot(prices, self.investor.shares)

            if np.isnan(portfolio):
                portfolio = 0.

            self.investor.history.append(portfolio)
            self.investor.invested_history.append(self.investor.invested)

            if self.investor.invested == 0:
                ror = 0
            else:
                ror = (portfolio - self.investor.invested) / self.investor.invested
            self.investor.ror_history.append(ror)

            if day % self.investor.dca.period == 0:
                self.investor.cash += self.investor.dca.cash
                self.investor.invested += self.investor.dca.cash

                portfolio = self.investor.cash + np.dot(prices, self.investor.shares)
                c = np.multiply(self.investor.dist, portfolio)
                c = np.subtract(c, self.tr_cost)
                s = np.divide(c, prices)
                s = np.floor(s)
                self.investor.shares = s
                self.investor.cash = portfolio - np.dot(self.investor.shares, prices) - len(s) * self.tr_cost

            day += 1
