import numpy as np
import pandas as pd
from scipy.stats import rankdata


def rolling_mean(data, period):
    rm = pd.rolling_mean(data, period)
    rm = rm[~np.isnan(rm)]
    return rm


def mean(value):
    value = np.mean(value)
    if np.isnan(value):
        return 0.
    return value


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
        self.rms_list = []
        self.means = []
        self.rank = 0.
        self.m = 0.
        self.std = 0.

    def compute_means(self):
        for i in range(1, 11):
            rms = rolling_mean(np.array(self.ror_history), i * 365)
            m = mean(rms)
            if m > 0:
                self.rms_list.append(rms)
                self.means.append(m.round(2))
            else:
                self.rms_list.append([0.])

        self.means = np.array(self.means)
        self.m = np.mean(self.means).round(2)
        if np.isnan(self.m):
            self.m = 0.
        self.std = np.std(self.means).round(4)
        if np.isnan(self.std):
            self.std = 0.

    def compute_rank(self):
        self.rank = (self.m + (1. - self.std)) / 2.


class BuyAndHoldInvestmentStrategy:
    def __init__(self, investor, tr_cost):
        self.investor = investor
        self.tr_cost = tr_cost

    def invest(self, data):
        if len(data.keys()) == 0:
            return

        self.investor.shares = np.zeros(len(data.keys()))

        day = 0

        for i in data.index:
            prices = data.loc[i].values
            if prices == 0.:
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
