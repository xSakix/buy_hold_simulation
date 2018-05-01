import pandas as pd
import numpy as np

prefix = 'mil_'

result_csv = 'evaluation_results/'+prefix+'evaluation_result.csv'
result_csv_out = 'evaluation_results/top_tier0_'+prefix+'evaluation_result.csv'
result_df = pd.read_csv(result_csv)

# else:
#     result_df = pd.DataFrame(
#         columns=['ticket', 'sim_interval_low', 'sim_interval_high', 'bayes_interval_low', 'bayes_interval_high',
#                  'rank'])


result_df = result_df[result_df.bayes_interval_low > -0.05]
result_df = result_df[result_df.bayes_interval_high > 0.3]
result_df = result_df.reset_index(drop=True)
ranked_df = result_df[['bayes_interval_low', 'bayes_interval_high']].rank(method='max')
for i in range(0, len(result_df)):
    result_df.loc[i, 'rank'] = ranked_df.loc[i].mean()
result_df.to_csv(result_csv_out, index=False)

