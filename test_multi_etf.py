import bah_multi_simulator as bahm
import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import timeit

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file

etfs = ['EWW', 'EWA', 'MDY', 'EWY', 'PNQI','XLE','SPY']
start_date = '1993-01-01'
end_date = '2017-12-31'

def compute_start_date(etf):
    inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')
    if etf in inception.ticket.values:
        return inception[inception.ticket == etf].inc_date.values[0]
    return '1993-01-01'


for etf in etfs:
    st_dt = compute_start_date(etf)
    if st_dt > start_date:
        start_date = st_dt

print(start_date)
print(end_date)


def rolling_mean(data, period):
    rm = pd.rolling_mean(data, period)
    rm = rm[~np.isnan(rm)]
    return rm


def mean(value):
    value = np.mean(value)
    if np.isnan(value):
        return 0.
    return value


def compute_multi_etf(etfs):
    df_adj_close = load_all_data_from_file('etf_data_adj_close.csv', start_date, end_date)
    dca = bahm.DCA(30, 300.)
    investor = bahm.Investor(etfs, np.full(len(etfs), 1.0 / len(etfs)), dca)
    sim = bahm.BuyAndHoldInvestmentStrategy(investor, 2.)
    print(df_adj_close[etfs].corr())
    sim.invest(df_adj_close[etfs], etfs)
    investor.compute_means()

    print(etfs)
    print('invested:' + str(investor.invested_history[-1]))
    print('value gained:' + str(investor.history[-1]))
    print('ror:' + str(investor.ror_history[-1]))
    print('mean:' + str(investor.m))
    print('std:' + str(investor.std))
    for rms in investor.means:
        print(str(rms))

    print('-'*80)

    return investor


def compute_one_etf(etf):

    df_adj_close = load_all_data_from_file('etf_data_adj_close.csv', start_date, end_date)
    dca = bah.DCA(30, 300.)
    investor = bah.Investor(etf, np.full(len(etf), 1.0 / len(etf)), dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(df_adj_close[etf])
    investor.compute_means()


    print(etf)
    print('invested:' + str(investor.invested_history[-1]))
    print('value gained:' + str(investor.history[-1]))
    print('ror:' + str(investor.ror_history[-1]))
    print('mean:' + str(investor.m))
    print('std:' + str(investor.std))
    for rms in investor.means:
        print(str(rms))
    print('-'*80)

    return investor

bah_investor = compute_multi_etf(etfs)

investors = []
for etf in etfs:
    investors.append(compute_one_etf([etf]))

plt.plot(bah_investor.invested_history, 'C1')
plt.plot(bah_investor.history, color='black')
legend = ['invested multi', 'value multi']

for etf in etfs:
    legend.append(etf)

for investor in investors:
    plt.plot(investor.history)

plt.legend(legend)

plt.show()

plt.plot(bah_investor.ror_history,color='black')
for investor in investors:
    plt.plot(investor.ror_history)

legend = [ 'ror multi']

for etf in etfs:
    legend.append(etf)

plt.legend(legend)

plt.show()

