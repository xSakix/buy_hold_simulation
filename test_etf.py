import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import timeit

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file



def rolling_mean(data, period):
    rm = pd.rolling_mean(data, period)
    rm = rm[~np.isnan(rm)]
    return rm


def mean(value):
    value = np.mean(value)
    if np.isnan(value):
        return 0.
    return value


def compute_one_etf(etf):
    start_date, end_date = compute_dates(etf)

    print(start_date)
    df_adj_close = load_all_data_from_file('etf_data_adj_close.csv', start_date, end_date)
    dca = bah.DCA(30, 300.)
    investor = bah.Investor(etf, np.full(len(etf), 1.0 / len(etf)), dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(df_adj_close[etf])
    investor.compute_means()


    _, ax = plt.subplots(3, 1)
    for rms in investor.rms_list:
        ax[2].plot(rms)

    print('invested:' + str(investor.invested_history[-1]))
    print('value gained:' + str(investor.history[-1]))
    print('ror:' + str(investor.ror_history[-1]))
    print('mean:' + str(investor.m))
    print('std:' + str(investor.std))
    for rms in investor.means:
        print(str(rms))

    ax[0].plot(np.log(df_adj_close[etf]))
    ax[0].plot(np.log(sim.investor.invested_history))
    ax[0].plot(np.log(sim.investor.history))
    # ax[0].plot(sim.investor.history)
    ax[1].plot(sim.investor.ror_history)
    ax[0].legend(['nav', 'invested', 'value'])
    ax[1].legend(['RoR'])

    plt.show()


def compute_dates(etf):
    start_date = '1993-01-01'
    end_date = '2017-12-31'
    inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')
    for anEtf in etf:
        if etf in inception.ticket.values:
            inception_date = inception[inception.ticket == anEtf].inc_date.values[0]
            if inception_date > start_date:
                start_date = inception_date
    return start_date,end_date


compute_one_etf(['SPYG'])
etf = ['SPY']
start_date, end_date = compute_dates(etf)

# def call_load_data():
#     load_data(etf, start_date, end_date)


# t = timeit.Timer(call_load_data).timeit(10)
# print(t)

# df_open, df_close, df_high, df_low, df_adj_close = load_data(etf, start_date, end_date)
#
# def call_sim():
#     dca = bah.DCA(30, 300.)
#     investor = bah.Investor(etf, np.full(len(etf), 1.0 / len(etf)), dca)
#     sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
#     sim.invest(df_adj_close)
#     investor.compute_means()
#
# t = timeit.Timer(call_sim).timeit(1000)
# print(t/1000.)
