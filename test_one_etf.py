import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file

import concurrent.futures
import time

current_millis = lambda: int(round(time.time() * 1000))

print('starting to load data')
prefix = 'xetra_'
start_date = '1993-01-01'
end_date = '2017-12-31'
df_adj_close = load_all_data_from_file(prefix+'etf_data_adj_close.csv', start_date, end_date)

if prefix == '':
    inception = pd.read_csv('../etf_data/etf_inc_date.csv', sep=';')
else:
    inception = None

with open('../etf_data/'+prefix+'etfs.txt', 'r') as fd:
    etf_list = list(fd.read().splitlines())

etf_list = list(set(etf_list))

print('data loaded')


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
    print(etf)
    result = etf[0]

    if inception is not None:
        inception_date = inception[inception.ticket == etf[0]].inc_date.values[0]
        data = df_adj_close[df_adj_close.Date > inception_date][etf]
    else:
        data = df_adj_close[etf]

    dca = bah.DCA(30, 300.)
    investor = bah.Investor(etf, [1.0], dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(data)
    investor.compute_means()
    result += ';' + str(investor.invested_history[-1])
    result += ';' + str(investor.history[-1])
    result += ';' + str(investor.ror_history[-1])
    result += ';' + str(investor.m)
    result += ';' + str(investor.std)
    for rms in investor.means:
        result += ';' + str(rms)
    result += '\n'
    print(result)

    with open(results, 'a+') as fd:
        fd.write(result)


results = 'results/'+prefix+'result.csv'
if os.path.isfile(results):
    os.remove(results)

with open(results, 'a+') as fd:
    headers = 'ticket;invested;value;ror;mean;std'
    for i in range(1, 11):
        headers += ';ma ror ' + str(i) + ' years'

    fd.write(headers + '\n')

cur = current_millis()


with concurrent.futures.ThreadPoolExecutor() as executor:
    for etf in etf_list:
        try:
            executor.submit(compute_one_etf,[etf], inception, results)
        except:
            print(etf + ' not processed')
    executor.shutdown(True)


print('time:'+str((current_millis()-cur)/1000.)+' s')