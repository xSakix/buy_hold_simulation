import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from simple_buy_and_hold_sim import BuyAndHoldInvestmentStrategy, SimpleBuyAndHoldMultiple

sys.path.insert(0, '../etf_data')
from etf_data_loader import load_all_data_from_file2

# tickets = ['6AQQ.DE',
#            'SPY1.DE',
#            'EXS3.DE',
#            'SXRJ.DE',
#            'SPYK.DE',
#            'LYYZ.DE',
#            'C065.DE',
#            'HNDX.DE',
#            'SXRU.DE',
#            'C073.DE',
#            'X026.DE'
#            ]
# tickets = ['DBPG.DE',
#            'IUES.L',
#            'AGGH.L',
#            'IFSW.L',
#            'RBOT.L',
#            'IAUS.L',
#            'EIMI.L',
#            ]
tickets = ['ANX.MI',
           'SWDA.MI',
           'SPY5.MI'
           ]
start_date = '2010-01-01'
end_date = '2018-06-15'

prefix = 'mil_'


def clean_data(df_adj_close, tickets):
    top = df_adj_close.index.max()
    found = False

    for ticket in tickets:
        for index in df_adj_close.index:
            if df_adj_close.loc[index, ticket] == 0.:
                for i in range(index, top + 1):
                    try:
                        if df_adj_close.loc[i, ticket] > 0.:
                            df_adj_close.loc[index, ticket] = df_adj_close.loc[i, ticket]
                            found = True
                            break
                    except:
                        continue
                if not found:
                    for i in range(index, 0, -1):
                        try:
                            if df_adj_close.loc[i, ticket] > 0.:
                                df_adj_close.loc[index, ticket] = df_adj_close.loc[i, ticket]
                                break
                        except:
                            continue
                found = False

    return df_adj_close


df_adj_close = load_all_data_from_file2(prefix + 'etf_data_adj_close.csv', start_date, end_date)
# df_adj_close2 = load_all_data_from_file('lse_etf_data_adj_close.csv', start_date, end_date)

# etf_1 = []
# etf_2 = []
# for ticket in tickets:
#     if ticket in df_adj_close.keys():
#         etf_1.append(ticket)
#     elif ticket in df_adj_close2.keys():
#         etf_2.append(ticket)

df_adj_close = df_adj_close.fillna(0.)
df_adj_close = clean_data(df_adj_close, tickets)

# df_adj_close2 = df_adj_close2.fillna(0.)
# df_adj_close2 = clean_data(df_adj_close2, etf_2)


def compute_multi_etf(etfs):
    sim = SimpleBuyAndHoldMultiple(tickets=etfs)
    print(df_adj_close[etfs].corr())
    # print(df_adj_close2[etf_2].corr())
    # sim.invest([df_adj_close[etf_1], df_adj_close2[etf_2]])
    sim.invest([df_adj_close[etfs]])

    print(etfs)
    print('invested:' + str(sim.investor.invested))
    print('value gained:' + str(sim.investor.gains))
    print('ror:' + str(sim.investor.returns))

    print('*' * 80)
    for i in range(len(sim.strategies)):
        print('ticket: '+sim.tickets[i])
        print('invested:' + str(sim.strategies[i].investor.invested))
        print('value gained:' + str(sim.strategies[i].investor.gains))
        print('ror:' + str(sim.strategies[i].investor.returns))

    print('-' * 80)

    return sim.investor


def compute_one_etf(etf):
    bah = BuyAndHoldInvestmentStrategy()
    bah.invest(df_adj_close[etf])

    # if etf[0] in df_adj_close.keys():
    #     bah.invest(df_adj_close[etf])
    # elif etf[0] in df_adj_close2.keys():
    #     bah.invest(df_adj_close2[etf])

    print(etf)
    print('invested:' + str(bah.investor.invested))
    print('value gained:' + str(bah.investor.gains))
    print('ror:' + str(bah.investor.returns))
    print('-' * 80)

    return bah.investor


bah_investor = compute_multi_etf(tickets)

investors = []
for etf in tickets:
    investors.append(compute_one_etf([etf]))

# investors.append(compute_one_etf(tickets))

# plt.plot(bah_investor.invested_history, 'C1')
# plt.plot(bah_investor.history, color='black')
# legend = ['invested multi', 'value multi']
#
# for etf in tickets:
#     legend.append(etf)
#
# legend.append(str(tickets))
#
# for investor in investors:
#     plt.plot(investor.history)
#
# plt.legend(legend)
#
# plt.show()
#
# plt.plot(bah_investor.ror_history, color='black')
# for investor in investors:
#     plt.plot(investor.ror_history)
#
# legend = ['ror multi']
#
# for etf in tickets:
#     legend.append(etf)
# legend.append(str(tickets))
#
# plt.legend(legend)
#
# plt.show()
