import pandas as pd
import os


def load_ranked(prefix=''):
    file = 'results/' + prefix + 'ranked_result.csv'
    if not os.path.isfile(file):
        file = '../buy_hold_simulation/' + file

    data = pd.read_csv(file)
    return data.sort_values(by=['rank'], ascending=False)


def test():
    ranked = load_ranked()
    ranked.to_csv('results/pyranked.csv')

test()