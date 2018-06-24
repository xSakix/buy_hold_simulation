import os

import pandas as pd

df = pd.read_csv('evaluation_results/mil_evaluation_result_2.csv')

df = df.sort_values(by=['rank'], ascending=False)

userdir = os.path.expanduser('~')

web_dir = userdir + '/Web/xSakix.github.io'

df = df[['rank', 'ticket', 'bayes_interval_low', 'bayes_interval_high']]
df = df.rename(index=str, columns={'bayes_interval_low': 'lower RoR', 'bayes_interval_high': 'upper RoR'})
df = df.head(10)

result_html = web_dir + '/mil_evaluation_result_2.html'
df.to_html(result_html, index=False, classes='pure-table pure-table-bordered')


df = pd.read_csv('evaluation_results/mil_evaluation_result_2.csv')

df = df.sort_values(by=['bayes_interval_high'], ascending=False)

df = df[['rank', 'ticket', 'bayes_interval_low', 'bayes_interval_high']]
df = df.rename(index=str, columns={'bayes_interval_low': 'lower RoR', 'bayes_interval_high': 'upper RoR'})
df = df.head(10)
result_top_risk_html = web_dir + '/mil_top10_risk.html'
df.to_html(result_top_risk_html, index=False, classes='pure-table pure-table-bordered')


template_start = '''<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
          integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/grids-responsive-min.css">
</head>
<body>

<div class="banner"> 
    <h1 class="banner-head"> ETF EU (Borsa-Italia)rankings</h1> 
    <pre>(Without warranty of any kind. Please use your own judgement...)</pre>     
    <p>
    ...By evaluating B&H simulations of Borsa Italia listed ETFs on random interval date data, I gathered
    data about possible RoR(rate of returns). Then I used these results in a probabilistic model and simulated
    and sampled given results by MCMC method...
    </p>
</div> 

<div id="layout" class="pure-g">
    <div class="content pure-u-1 pure-u-md-1-2">
            <h2 class="post-title">Top 10 ETFs by ranking</h2>
            <pre> (Should be low risk investments...)</pre>
            <div>
'''

template_mid = '''
            </div>
    </div>
    <div class="content pure-u-1 pure-u-md-1-2">
            <h2 class="post-title">Top 10 ETFs by upper RoR</h2>
            <pre> (Should be high risk and high reward investments...)</pre>
            <div>            
'''

template_end = '''
            </div>
    </div>
</div>
</body>
</html>
'''

html = open(result_html, 'r', encoding='utf-8').read()

html2 = open(result_top_risk_html, 'r', encoding='utf-8').read()

html = template_start + html + template_mid+html2+template_end

with open(result_html, 'w', encoding='utf-8') as fd:
    fd.write(html)

os.remove(result_top_risk_html)

