import numpy as np
from _datetime import datetime
from simple_buy_and_hold_sim import BuyAndHoldInvestmentStrategy
import pymc3 as pm
import sys

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file
from result_loader import load_ranked
import os
import pandas as pd


def gen_random_date(year_low, year_high):
    y = np.random.randint(year_low, year_high)
    m = np.random.randint(1, 12)
    d = np.random.randint(1, 28)
    return datetime(year=y, month=m, day=d)


def get_data_random_dates(df_adj_close, min_year, max_year):
    rand_start = gen_random_date(min_year, max_year)
    rand_end = gen_random_date(min_year, max_year)
    if rand_start > rand_end:
        tmp = rand_start
        rand_start = rand_end
        rand_end = tmp
    data = df_adj_close[df_adj_close['Date'] > str(rand_start)]
    data = data[data['Date'] < str(rand_end)]

    return data


def clean_data(df_adj_close):
    top = df_adj_close.index.max()

    for index in df_adj_close.index:
        if df_adj_close.loc[index, ticket] == 0.:
            for i in range(index, top + 1):
                if df_adj_close.loc[i, ticket] > 0.:
                    df_adj_close.loc[index, ticket] = df_adj_close.loc[i, ticket]
                    break
    return df_adj_close


start_date = '1993-01-01'
end_date = '2018-04-08'
prefix = 'mil_'

df_adj_close = load_all_data_from_file(prefix + 'etf_data_adj_close.csv', start_date, end_date)

np.warnings.filterwarnings('ignore')

prefix = 'mil_'
etf_list = []
with open('../etf_data/' + prefix + 'etfs.txt', 'r') as fd:
    etf_list = list(fd.read().splitlines())

etf_list = list(set(etf_list))

MAX_ITER = 1000

result_csv = 'evaluation_results/' + prefix + 'experimental_evaluation_result.csv'
if os.path.isfile(result_csv):
    result_df = pd.read_csv(result_csv)
else:
    result_df = pd.DataFrame(
        columns=['ticket', 'sim_interval_low', 'sim_interval_high', 'bayes_interval_low', 'bayes_interval_high',
                 'rank'])

counter = 0

for ticket in etf_list:
    if ticket in result_df['ticket'].values:
        continue
    print('-' * 80)
    print(ticket)

    try:
        df_ticket_data = df_adj_close[['Date', ticket]]
    except:
        print('failed to find ticket: ' + ticket)
        continue
    df_ticket_data = df_ticket_data[df_ticket_data[ticket] > 0.]
    df_ticket_data = df_ticket_data.reindex()

    date_data = df_ticket_data.Date
    try:
        min_year = datetime.strptime(date_data.min(), '%Y-%M-%d').year
    except:
        print(ticket + ' has no date data!')
        continue

    max_year = datetime.strptime(date_data.max(), '%Y-%M-%d').year
    if min_year >= max_year:
        print('%s not processed because of min_year >= max_year' % (ticket))
        continue

    returns = np.empty((MAX_ITER,))
    i = 0
    failed = 0
    while i < MAX_ITER:
        data = get_data_random_dates(df_ticket_data, min_year, max_year)
        prices = np.nan_to_num(np.array(data[ticket].values))
        prices = prices[prices > 0.]
        if len(prices) == 0:
            continue
        price_returns = []
        for t in range(1, len(prices)):
            price_returns.append(np.log(prices[t] / prices[t - 1]))
        price_returns = np.array(price_returns)
        if len(price_returns) == 0:
            continue
        returns[i] = np.cumsum(price_returns)[-1]
        # print('returns:' + str(returns[i]))
        i += 1

    if failed > MAX_ITER:
        print('%s cant be computed!' % ticket)
        continue

    hpd_sim = pm.hpd(returns, alpha=0.11)
    print('89 percentile results from b&h simulations:' + str(hpd_sim))
    try:
        with pm.Model() as model:
            mu = pm.Normal('mu', mu=np.mean(returns), sd=np.std(returns))
            sigma = pm.Uniform('sigma', lower=0, upper=np.std(returns))
            ret = pm.Normal('ret', mu=mu, sd=sigma, observed=returns)
            trace_model = pm.sample(1000, tune=2000)

        samples_bah = pm.sample_ppc(trace_model, size=10000, model=model)
        hpd_sampled = pm.hpd(samples_bah['ret'], alpha=0.11)

        mean_hpd_bayes = np.mean(hpd_sampled, axis=0)
        print('mean results of 89 percentile interval from bayesian model: ' + str(mean_hpd_bayes))
    except:
        print('failed to compute bayesian analysis')
        mean_hpd_bayes = hpd_sim

    result_df = result_df.append({
        'ticket': ticket,
        'sim_interval_low': hpd_sim[0],
        'sim_interval_high': hpd_sim[1],
        'bayes_interval_low': mean_hpd_bayes[0],
        'bayes_interval_high': mean_hpd_bayes[1]
    }, ignore_index=True)

    result_df.to_csv(result_csv, index=False)

ranked_df = result_df[['bayes_interval_low', 'bayes_interval_high']].rank(method='max')
for i in range(0, len(result_df)):
    result_df.loc[i, 'rank'] = ranked_df.loc[i].mean()
result_df.to_csv(result_csv, index=False)
