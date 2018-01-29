import numpy as np
import pandas as pd
from scipy.stats import rankdata

data = pd.read_csv('results/result.csv',sep=';')
rank1 = rankdata(data['mean'],method='max')
print(len(rank1))
rank2 = 100.*data['std']
rank = rank1-rank2
print(len(data))
print(len(rank))
data['rank'] = rank
data.to_csv('results/ranked_result.csv')
