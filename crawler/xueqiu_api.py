from crawler.cache import get_cache, save_cache
import datetime
import requests
import time
import json


# 可转债
# https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ128040&begin=1555517900000&period=day&count=-1
def get_bond_his_rate(stockcode, date, ifcache=True):

    dict = get_cache()
    if ifcache and (stockcode, date) in dict.keys():
        #print("hit")
        return dict[(stockcode, date)]

    timestamp = int(time.mktime(date.timetuple()) * 1000)
    #print(timestamp)

    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=$stockcode&begin=$timestamp&period=day&count=-1"
    url = url.replace("$stockcode", stockcode).replace("$timestamp", str(timestamp))
    #print(url)

    session = requests.Session()
    session.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    session.get('https://xueqiu.com/')
    r = session.get(url)
    #print(r.content)
    j = json.loads(r.content)

    date_get = datetime.datetime.fromtimestamp(j['data']['item'][0][0] / 1000.0).date()
    close = float(j['data']['item'][0][5])

    if date_get == date:
        #print("insert", stockcode, date, close)
        dict[stockcode, date] = close

    save_cache(dict)
    if (stockcode, date) in dict.keys():
        return dict[stockcode, date]
    else:
        return -1


if __name__ == "__main__":
    # 可转债
    print(get_bond_his_rate("SZ128039", datetime.datetime.strptime("2019/4/9", '%Y/%m/%d').date()))
