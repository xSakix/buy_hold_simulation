import os
import pandas as pd


def transform_to_html(infile='evaluation_results/mil_evaluation_result_3.csv', outfile='mil_evaluation_result'):
    df = pd.read_csv(infile)

    df = df.sort_values(by=['rank'], ascending=False)

    userdir = os.path.expanduser('~')

    web_dir = userdir + '/Web/xSakix.github.io'

    df = df[['rank', 'ticket', 'bayes_interval_low', 'bayes_interval_high']]
    df = df.rename(index=str, columns={'bayes_interval_low': 'lower RoR', 'bayes_interval_high': 'upper RoR'})
    df = df.head(10)

    result_html = web_dir + '/' + outfile + '.html'
    df.to_html(result_html, index=False, classes='pure-table pure-table-bordered')

    df = pd.read_csv(infile)

    df = df.sort_values(by=['bayes_interval_high'], ascending=False)

    df = df[['rank', 'ticket', 'bayes_interval_low', 'bayes_interval_high']]
    df = df.rename(index=str, columns={'bayes_interval_low': 'lower RoR', 'bayes_interval_high': 'upper RoR'})
    df = df.head(10)
    result_top_risk_html = web_dir + '/mil_top10_risk.html'
    df.to_html(result_top_risk_html, index=False, classes='pure-table pure-table-bordered')

    template_start = '''<html>
    <head>
        <title>ETF EU rankings</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">    
        <meta name="description" contant="By evaluating B&H simulations of EU ETFs on random interval date data, I gathered
        data about possible RoR(rate of returns). Then I used these results in a probabilistic model and simulated
        and sampled given results by MCMC method">
        <meta name="keywords" content="Top ETF, Top UCITS ETF, ETF ranking, ETF EU, ETF, ETF suggestion">      
        <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
              integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
        <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/grids-responsive-min.css">
    </head>
    <body>
    
    <div class="banner"> 
        <h1 class="banner-head"> ETF EU rankings</h1> 
        <pre>(Without warranty of any kind. Please use your own judgement...)</pre>     
        <p>
        ...By evaluating B&H simulations of EU ETFs on random interval date data, I gathered
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

    html = template_start + html + template_mid + html2 + template_end

    with open(result_html, 'w', encoding='utf-8') as fd:
        fd.write(html)

    os.remove(result_top_risk_html)


def push_changes():
    import git
    userdir = os.path.expanduser('~')
    web_dir = userdir + '/Web/xSakix.github.io'
    repo = git.Repo(web_dir)
    _commit = repo.commit()
    _commit.message = 'update...'


def generate_index():
    userdir = os.path.expanduser('~')
    web_dir = userdir + '/Web/xSakix.github.io'
    results = [file for file in os.listdir(web_dir) if 'mil_evaluation_result.html' in file]
    result_list = {}
    for file in results:
        abs_file = web_dir + '/' + file
        time = os.path.getctime(abs_file)
        result_list[datetime.date.fromtimestamp(time)] = file

    sorted_keys = sorted(result_list.keys())[::-1]

    template_start = '''<html>
    <head>
        <title>ETF EU rankings</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">    
        <meta name="description" contant="By evaluating B&H simulations of EU ETFs on random interval date data, I gathered
        data about possible RoR(rate of returns). Then I used these results in a probabilistic model and simulated
        and sampled given results by MCMC method">
        <meta name="keywords" content="Top ETF, Top UCITS ETF, ETF ranking, ETF EU, ETF, ETF suggestion">      
        <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
              integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
        <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/grids-responsive-min.css">
    </head>
    <body>

    <div class="banner"> 
        <h1 class="banner-head"> ETF EU rankings</h1> 
        <pre>(Without warranty of any kind. Please use your own judgement...)</pre>     
        <p>
        ...By evaluating B&H simulations of EU ETFs on random interval date data, I gathered
        data about possible RoR(rate of returns). Then I used these results in a probabilistic model and simulated
        and sampled given results by MCMC method...
        </p>
    </div> 

        <div>
            <p>
            Results by date:
            </p>
            <ul>
            '''
    u_list = ''
    for key in sorted_keys:
        u_list += '<li><a href="{}"><pre>{}</pre></a></li>\n'.format(result_list[key], str(key))

    template_end = '''
            </ul>
        
        </div>
    </div>
    </body>
    </html>
    '''
    html = template_start+u_list+template_end
    with open(web_dir+'/index.html', 'w', encoding='utf-8') as fd:
        fd.write(html)

if __name__ == '__main__':
    import datetime

    outputfile = str(datetime.date.today()).replace('-', '_') + '_mil_evaluation_result'
    transform_to_html(infile='evaluation_results/mil_evaluation_result_10.csv',outfile=outputfile)
    generate_index()
