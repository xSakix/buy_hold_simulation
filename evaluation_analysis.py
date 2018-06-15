import pandas as pd
import numpy as np

prefix = 'mil_'

result_csv = 'evaluation_results/'+prefix+'evaluation_result_1.csv'
result_csv_out = 'evaluation_results/top_tier2_'+prefix+'evaluation_result_1.csv'
result_df = pd.read_csv(result_csv)

print(len(result_df))

result_df = result_df[result_df.bayes_interval_low > -0.2]
print(len(result_df))
result_df = result_df[result_df.bayes_interval_high > 0.8]
print(len(result_df))
result_df = result_df.reset_index(drop=True)
print(len(result_df))
ranked_df = result_df[['bayes_interval_low', 'bayes_interval_high']].rank(method='max')
for i in range(0, len(result_df)):
    result_df.loc[i, 'rank'] = ranked_df.loc[i].mean()
result_df.to_csv(result_csv_out, index=False)

