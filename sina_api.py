import datetime
import requests
import pickle
import random
import json
import datetime
from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup

his_data_file = "his_data.pkl"
def print_cache_all():
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}
    for (stockcode, date) in dict.keys():
        print(stockcode, date, dict[(stockcode, date)])

# A股+场内基金
def get_stock_his_price(stockcode, date, cache=True):
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}

    if cache and (stockcode, date) in dict.keys():
        print("hit")
        return dict[(stockcode, date)]

    url = "http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/" + \
        "$stockcode.phtml?year=$year&jidu=$jidu"
    url = url.replace("$stockcode", stockcode).replace("$year", str(date.year)) \
        .replace("$jidu", str((date.month + 2)//3))
    print(url)
    r = requests.get(url)
    result = r.content.decode('GBK')
    bs = BeautifulSoup(result, "html.parser")
    table = bs.find('table', id='FundHoldSharesTable')
    #print(table)
    for idx, tr in enumerate(table):
        if idx >= 5 and idx % 2 == 1:
            #print(idx, tr)
            for idx2, td in enumerate(tr):
                if idx2 == 1:
                    time = datetime.datetime.strptime(td.text.strip(), '%Y-%m-%d').date()
                elif idx2 == 7:
                    price = float(td.text.strip())
            print("insert", time, price)
            dict[stockcode, time] = price

    with open(his_data_file, 'wb') as f:
        pickle.dump(dict, f)

    if (stockcode, date) in dict.keys():
        return dict[stockcode, date]
    else:
        return -1

# 港股
def get_hkstock_his_price(stockcode, date, cache=True):
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}

    if cache and (stockcode, date) in dict.keys():
        print("hit")
        return dict[(stockcode, date)]

    url = "http://stock.finance.sina.com.cn/hkstock/history/$stockcode.html"
    params = {"year": str(date.year), "season": str((date.month + 2) // 3)}
    url = url.replace("$stockcode", stockcode[2:])

    r = requests.post(url, data=params)
    #print(r.request.body)

    result = r.content.decode('GBK')
    #print(result)
    bs = BeautifulSoup(result, "html.parser")
    table = bs.find('tbody')
    #print(table)
    for idx, tr in enumerate(table):
        if idx >= 3 and idx % 2 == 1:
            # print(idx, tr)
            for idx2, td in enumerate(tr):
                if idx2 == 1:
                    time = datetime.datetime.strptime(td.text.strip(), '%Y%m%d').date()
                elif idx2 == 3:
                    price = float(td.text.strip())
            print("insert", time, price)
            dict[stockcode, time] = price
    with open(his_data_file, 'wb') as f:
        pickle.dump(dict, f)

    if (stockcode, date) in dict.keys():
        return dict[stockcode, date]
    else:
        return -1

# 场外基金
# http://stock.finance.sina.com.cn/fundInfo/view/FundInfo_LSJZ.php?symbol=110033
def get_fund_his_price(stockcode, date, cache=True):
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}

    if cache and (stockcode, date) in dict.keys():
        print("hit")
        return dict[(stockcode, date)]

    url = "http://stock.finance.sina.com.cn/fundInfo/api/openapi.php/CaihuiFundInfoService.getNav?symbol=$stockcode&datefrom=$datefrom&dateto=$dateto&page=1"
    url = url.replace("$stockcode", stockcode[2:]).replace("$dateto", date.strftime("%Y-%m-%d")).replace("$datefrom",  (date - relativedelta(months=+2)).strftime("%Y-%m-%d"))
    #print(url)
    r = requests.get(url)
    #print(r.content)
    j = json.loads(r.content)
    #print(j)

    for data in j['result']['data']['data']:
        time = datetime.datetime.strptime(data['fbrq'], '%Y-%m-%d %H:%M:%S').date()
        price = data['jjjz']
        print("insert", time, price)
        dict[stockcode, time] = price

    with open(his_data_file, 'wb') as f:
        pickle.dump(dict, f)

    if (stockcode, date) in dict.keys():
        return dict[stockcode, date]
    else:
        return -1

if __name__ == "__main__":
    #print(datetime.datetime.strptime("2019/3/1", '%Y/%m/%d').date())
    # A股
    print(get_stock_his_price("600029", datetime.datetime.strptime("2019/3/1", '%Y/%m/%d').date()))
    # 场内基金
    print(get_stock_his_price("501029", datetime.datetime.strptime("2019/3/1", '%Y/%m/%d').date()))
    # 港股
    print(get_hkstock_his_price("hk00981", datetime.datetime.strptime("2019/4/9", '%Y/%m/%d').date()))
    # 场外基金
    print(get_fund_his_price("of110033", datetime.datetime.strptime("2019/4/9", '%Y/%m/%d').date()))
    print_cache_all()
    #TODO 可转债
