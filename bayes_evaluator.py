import bah_simulator as bah
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import timeit

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file

import pymc3 as pm
import seaborn as sns

print('starting to load data')
prefix = ''
start_date = '1993-01-01'
end_date = '2017-12-31'
df_adj_close = load_all_data_from_file(prefix + 'etf_data_adj_close.csv', start_date, end_date)


def compute_one_etf(etf):
    dca = bah.DCA(30, 300.)
    investor = bah.Investor(etf, np.full(len(etf), 1.0 / len(etf)), dca)
    sim = bah.BuyAndHoldInvestmentStrategy(investor, 2.)
    sim.invest(df_adj_close[etf])
    investor.compute_means()

    _, ax = plt.subplots(3, 1)
    for rms in investor.rms_list:
        ax[2].plot(rms)

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

    return investor


etf = ['SPY']

investor = compute_one_etf(etf)
print('invested:' + str(investor.invested_history[-1]))
print('value gained:' + str(investor.history[-1]))
print('ror:' + str(investor.ror_history[-1]))
print('mean:' + str(investor.m))
print('std:' + str(investor.std))

plt.plot(df_adj_close[etf], investor.ror_history, 'C0o')
plt.show()

data = df_adj_close[etf].values
ror = np.array(investor.ror_history)
mean = data.mean()
std = data.std()
print('mean of prices: ' + str(mean))
print('std of prices: ' + str(std))

data_list = []
for d in data:
    if len(d) > 0:
        data_list.append(d[0])
    else:
        data_list.append(d)

data = np.array(data_list)
# data = data - np.mean(data)

sns.kdeplot(data)
plt.show()

sns.kdeplot(ror)
plt.show()

df = pd.DataFrame({'data':data,'ror':ror})
print(df.corr().round(2))

with pm.Model() as model:
    alpha = pm.Normal(name='alpha', mu=mean, sd=std)
    beta = pm.Normal(name='beta', mu=0, sd=100)
    sigma = pm.Uniform(name='sigma', lower=0., upper=std)
    mu = pm.Deterministic('mu', alpha + beta * data)
    ret = pm.Normal(name='returns', mu=mu, sd=sigma, observed=ror)
    trace_model = pm.sample(1000, tune=1000)

pm.traceplot(trace_model)
plt.show()

data_seq = np.arange(min(data), max(data))
mu_pred = np.zeros((len(data_seq), len(trace_model) * trace_model.nchains))
for i, data_point in enumerate(data_seq):
    mu_pred[i] = trace_model['alpha'] + trace_model['beta'] * data_point

plt.plot(data_seq, mu_pred, 'C0.', alpha=0.1)
plt.xlabel('etf price data')
plt.ylabel('returns')
plt.show()

mu_mean = mu_pred.mean(1)
mu_hpd = pm.hpd(mu_pred.T, alpha=0.11)
print('mean mu: ' + str(mu_mean))
print('mu hpd 89%: ' + str(mu_hpd))

_, (ax0, ax1) = plt.subplots(1, 2)
ax0.plot(data_seq, mu_pred, 'C0.', alpha=0.1)
ax1.scatter(data, ror)
ax1.plot(data_seq, mu_mean, 'C2')
ax1.fill_between(data_seq, mu_hpd[:, 0], mu_hpd[:, 1], color='C2', alpha=0.25)
plt.show()

# simulating returns from model
returns_pred = pm.sample_ppc(trace_model, 10000, model)
print(returns_pred)

# sumary for 89%
returns_pred_hpd = pm.hpd(returns_pred['returns'], alpha=0.11)
print(returns_pred_hpd)

#before plot sort is required
idx = np.argsort(data)
d_weight_ord = data[idx]
returns_pred_hpd = returns_pred_hpd[idx]

plt.scatter(data, ror)
plt.fill_between(data_seq, mu_hpd[:, 0], mu_hpd[:, 1], color='C2', alpha=0.25)
plt.fill_between(d_weight_ord, returns_pred_hpd[:, 0], returns_pred_hpd[:, 1], color='C2', alpha=0.25)
plt.plot(data_seq, mu_mean,color='black')
plt.show()