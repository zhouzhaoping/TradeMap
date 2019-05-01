#https://github.com/Alexdachen/ivix

import pandas as pd

shibor_rate = pd.read_csv('indexdata/shibor.csv',index_col=0,encoding='GBK')
options_data = pd.read_csv('indexdata/options.csv',index_col=0,encoding='GBK')
tradeday = pd.read_csv('indexdata/tradeday.csv',encoding='GBK')
true_ivix = pd.read_csv('indexdata/ivixx.csv',encoding='GBK')