import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_data

with open('../rebalancer/etfs.txt', 'r') as fd:
    etfs = list(fd.read().splitlines())

etfs = list(set(etfs))


def rolling_mean(data, period):
    rm = pd.rolling_mean(data, period)
    rm = rm[~np.isnan(rm)]
    return rm


def mean(value):
    value = np.mean(value)
    if np.isnan(value):
        return 0.
    return value


def compute_one_etf(etf, inception, results):
    result = etf

    start_date = '1993-01-01'
    end_date = '2017-12-31'

    if etf in inception.ticket.values:
        inception_date = inception[inception.ticket == etf].inc_date.values[0]
        if inception_date > start_date:
            start_date = inception_date

    df_open, df_close, df_high, df_low, df_adj_close = load_data([etf], start_date, end_date)
    dca = bah.DCA(30, 300.)
    investor = bah.Investor([1.0], dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(df_adj_close, df_high, df_low)
    means = []
    rms_list = []
    for i in range(1, 11):
        rms = rolling_mean(np.array(sim.investor.ror_history), i * 365)
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

    result += ';' + str(sim.investor.invested_history[-1])
    result += ';' + str(sim.investor.history[-1])
    result += ';' + str(sim.investor.ror_history[-1])
    result += ';' + str(m)
    result += ';' + str(std)
    for rms in rms_list:
        result += ';' + str(rms)
    result += '\n'

    with open(results, 'a+') as fd:
        fd.write(result)


results = 'results/result.csv'
if os.path.isfile(results):
    os.remove(results)

with open(results, 'a+') as fd:
    headers = 'ticket;invested;value;ror;mean;std'
    for i in range(1, 11):
        headers += ';ma ror ' + str(i) + ' years'

    fd.write(headers + '\n')

inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')

count = 1
for etf in etfs:
    try:
        print(str(count) + '/' + str(len(etfs)))
        count += 1
        compute_one_etf(etf, inception, results)
    except:
        print(etf + ' not processed')
