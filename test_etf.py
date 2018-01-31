import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_data



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
    start_date = '1993-01-01'
    end_date = '2017-12-31'

    inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')

    for anEtf in etf:
        if etf in inception.ticket.values:
            inception_date = inception[inception.ticket == anEtf].inc_date.values[0]
            if inception_date > start_date:
                start_date = inception_date

    print(start_date)

    df_open, df_close, df_high, df_low, df_adj_close = load_data(etf, start_date, end_date)
    dca = bah.DCA(30, 300.)
    investor = bah.Investor(np.full(len(etf), 1.0 / len(etf)), dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(df_adj_close, df_high, df_low)

    _, ax = plt.subplots(3, 1)

    means = []
    rms_list = []
    for i in range(1, 11):
        rms = rolling_mean(np.array(sim.investor.ror_history), i * 365)
        ax[2].plot(rms)
        m = mean(rms)
        if m > 0:
            rms_list.append(m.round(2))
            means.append(m.round(2))
        else:
            rms_list.append(0.)

    means = np.array(means)
    m = np.mean(means).round(2)
    if np.isnan(m):
        m = 0.
    std = np.std(means).round(2)
    if np.isnan(std):
        std = 0.

    print('invested:' + str(sim.investor.invested_history[-1]))
    print('value gained:' + str(sim.investor.history[-1]))
    print('ror:' + str(sim.investor.ror_history[-1]))
    print('mean:' + str(m))
    print('std:' + str(std))
    for rms in rms_list:
        print(str(rms))

    ax[0].plot(np.log(df_adj_close))
    ax[0].plot(np.log(sim.investor.invested_history))
    ax[0].plot(np.log(sim.investor.history))
    # ax[0].plot(sim.investor.history)
    ax[1].plot(sim.investor.ror_history)
    ax[0].legend(['nav', 'invested', 'value'])
    ax[1].legend(['RoR'])

    plt.show()


compute_one_etf(['PAK'])
