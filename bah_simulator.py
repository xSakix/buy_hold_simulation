import numpy as np


def load_high_low(df_high, df_low):
    if df_high is not None and df_low is not None:
        df_high_low = np.abs(df_high - df_low)

    return df_high_low


class DCA:
    def __init__(self, period=30, cash=300.):
        self.period = period
        self.cash = cash


class Investor:
    def __init__(self, dist, dca):
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

    def invest(self, df_open, df_high, df_low):
        df_high_low = load_high_low(df_high, df_low)

        if len(df_open.keys()) == 0:
            return

        self.investor.shares = np.zeros(len(df_open.keys()))

        day = 0

        for i in df_open.index:

            prices = df_open.loc[i]
            high_low = df_high_low.loc[i]
            high_low = np.array(high_low)

            portfolio = self.investor.cash + np.dot(prices, self.investor.shares)

            self.investor.history.append(portfolio)
            self.investor.invested_history.append(self.investor.invested)

            if self.investor.invested == 0:
                ror = 0
            else:
                ror = (portfolio-self.investor.invested)/self.investor.invested
            self.investor.ror_history.append(ror)

            if day % self.investor.dca.period == 0:

                self.investor.cash += self.investor.dca.cash
                self.investor.invested += self.investor.dca.cash

                portfolio = self.investor.cash + np.dot(prices, self.investor.shares)

                prices = compute_prices(high_low, prices)

                c = np.multiply(self.investor.dist, portfolio)
                c = np.subtract(c, self.tr_cost)
                s = np.divide(c, prices)
                s = np.floor(s)
                self.investor.shares = s
                self.investor.cash = portfolio - np.dot(self.investor.shares, prices) - len(s) * self.tr_cost

            day += 1


def compute_prices(high_low, prices):
    high_low = np.array(high_low)
    high_low[high_low <= 0.] = 0.001
    high_low[np.isnan(high_low)] = 0.001
    noise = np.random.normal(0, high_low)
    prices = np.add(prices, noise)

    return prices
