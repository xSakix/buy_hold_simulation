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

data = df_adj_close[etf].values
ror = np.array(investor.ror_history)

data_list = []
for d in data:
    if len(d) > 0:
        data_list.append(d[0])
    else:
        data_list.append(d)

data = np.array(data_list)

mean_data = data.mean()
std_data = data.std()

data_s = (data - mean_data) / std_data
data_s2 = data_s ** 2
data_s3 = data_s ** 3
data_s4 = data_s ** 4

print('mean of prices: ' + str(mean_data))
print('std of prices: ' + str(std_data))

plt.plot(data_s, investor.ror_history, 'C0o')
plt.title('nav to returns')
plt.xlabel('nav')
plt.ylabel('returns')
plt.show()

sns.kdeplot(data)
plt.title('distribution of nav')
plt.show()

sns.kdeplot(ror)
plt.title('distribution of returns')
plt.show()

df = pd.DataFrame({'data_s': data_s, 'ror': ror})
print(df.corr().round(2))

with pm.Model() as model:
    alpha = pm.Normal(name='alpha', mu=np.mean(ror), sd=np.std(ror))
    beta = pm.Normal(name='beta', mu=0, sd=10, shape=4)
    sigma = pm.Uniform(name='sigma', lower=min(ror), upper=max(ror))
    mu = pm.Deterministic('mu', alpha + beta[0] * data_s + beta[1] * data_s2+beta[2] * data_s3+beta[3] * data_s4)
    ret = pm.Normal(name='returns', mu=mu, sd=sigma, observed=ror)
    trace_model = pm.sample(1000, tune=2000)

print(pm.summary(trace_model, ['alpha', 'beta', 'sigma']))

pm.traceplot(trace_model, varnames=['alpha', 'beta', 'sigma'])
plt.title('model parameters')
plt.show()


mu_pred = trace_model['mu']
idx = np.argsort(data_s)
mu_hpd = pm.hpd(mu_pred, alpha=0.11)[idx]
ret_pred = pm.sample_ppc(trace_model, 200, model)
ret_pred_hpd = pm.hpd(ret_pred['returns'], alpha=0.11)[idx]

plt.plot(ror)
plt.plot(ret_pred_hpd)
plt.show()


plt.scatter(data_s, ror, c='C0', alpha=0.3)
plt.fill_between(data_s[idx], mu_hpd[:, 0], mu_hpd[:, 1], color='C2', alpha=0.25)
plt.fill_between(data_s[idx], ret_pred_hpd[:, 0], ret_pred_hpd[:, 1], color='C2', alpha=0.25)
plt.show()
