import numpy as np
import pandas as pd
from scipy.stats import rankdata

prefix = 'xetra_'

data = pd.read_csv('results/'+prefix+'result.csv',sep=';')
rank1 = rankdata(data['mean'],method='max')
print(len(rank1))
rank2 = 100.*data['std']
rank = rank1-rank2
print(len(data))
print(len(rank))
data['rank'] = rank

data['rank2'] = (data['mean'] +(1.- data['std']))/2.

data.to_csv('results/'+prefix+'ranked_result.csv')
