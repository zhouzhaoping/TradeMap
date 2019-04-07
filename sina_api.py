import datetime
import requests
import pickle
import random
import datetime

from bs4 import BeautifulSoup

his_data_file = "his_data.pkl"

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

if __name__ == "__main__":
    #print(datetime.datetime.strptime("2019/3/1", '%Y/%m/%d').date())
    #get_stock_his_price("600029", datetime.datetime.strptime("2019/3/1", '%Y/%m/%d').date())
    get_hkstock_his_price("hk00981", datetime.datetime.strptime("2019/4/7", '%Y/%m/%d').date())
