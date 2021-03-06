import baostock as bs
import pandas as pd
import requests
import json
import math
import random
import time
import html
import datetime


# http://baostock.com
def get_stock_price(stock_code, date):
    #### 登陆系统 ####
    lg = bs.login()

    rs = bs.query_history_k_data_plus(stock_code,
                                      "date,code,close",
                                      start_date=date, end_date=date,
                                      frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    print(result)
    #### 登出系统 ####
    bs.logout()
    return float(result['close'][0])


def get_fund_price(fund_code):
    url = "https://fundmobapi.eastmoney.com/FundMApi/FundBaseTypeInformation.ashx?&FCODE=$fund_code&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0"
    url = url.replace("$fund_code", fund_code)
    r = requests.get(url)
    result = r.content.decode('utf-8')
    #print(result)
    j = json.loads(result)
    return float(j['Datas']['DWJZ']), datetime.datetime.strptime(j['Datas']['FSRQ'], '%Y-%m-%d')


def get_sina_price(stock_code):
    url = "http://hq.sinajs.cn/list=$stock_code"
    # 00-深证A股，60-上证A股，300-创业板
    # 15、16、18-深证场内基金，50、51、52-上证场内基金
    # 12-深证转债，11-上证转债
    if stock_code[:2] == "hk":
        pass
    elif stock_code[:2] in {"60", "68", "50", "51", "52", "11", "13"}:# 13 for EB; 68 for 科创板
        stock_code = "sh" + stock_code
    elif stock_code[:2] in {"00", "30", "15", "16", "18", "12"}:
        stock_code = "sz" + stock_code
    elif stock_code[:2] in {"83"}: # for 新三板
        stock_code = "sb" + stock_code
    else:
        assert False, "stock code error"
    url = url.replace("$stock_code", stock_code)
    r = requests.get(url)
    print(url)
    result = r.content.decode('GBK')
    print(result)

    try:
        #print("try", "code", stock_code, "curprice", result.split(",")[3], result.split(",")[6], "date_now",
         #     result.split(",")[-4], "date_now", result.split(",")[-3], "date_now", result.split(",")[-2])

        if stock_code[:2] == "hk":
            curprice = result.split(",")[6]
        else:
            curprice = result.split(",")[3]

        if curprice == '0.000':
            print("停牌" + stock_code)
            curprice = result.split(",")[2]
        if stock_code[:5] == "sz300":
            date_now = datetime.datetime.strptime(result.split(",")[-4], '%Y-%m-%d')
        elif stock_code[:2] == "sh":
            date_now = datetime.datetime.strptime(result.split(",")[-4], '%Y-%m-%d')
        elif stock_code[:4] == "sz30":
            date_now = datetime.datetime.strptime(result.split(",")[-4], '%Y-%m-%d')
        elif stock_code[:2] == "sz":
            date_now = datetime.datetime.strptime(result.split(",")[-3], '%Y-%m-%d')
        elif stock_code[:2] == "sb":
            date_now = datetime.datetime.strptime(result.split(",")[-9], '%Y-%m-%d')
        else:
            date_now = datetime.datetime.strptime(result.split(",")[-2], '%Y/%m/%d')

        #print(stock_code, curprice, date_now)
    except:
        curprice = 100.0# todo 未上市的债券
        date_now = datetime.datetime.strptime("2021-01-31", '%Y-%m-%d')

    # 0股票名字；1今日开盘价；2昨日收盘价；3当前价格；4今日最高价；5今日最低价；6竞买价，即“买一”报价；7竞卖价，即“卖一”报价；
    # http://blog.sina.com.cn/s/blog_5dc29fcc0101dq5s.html
    #print(curprice)
    return float(curprice), date_now


def get_hk_rate():
    return 0.84061
    time_now = time.strftime("%Y%m%d", time.localtime())
    #print(time_now)
    response = requests.get(
        'http://query.sse.com.cn/commonSoaQuery.do?&jsonCallBack=jsonpCallback'
        + str(math.floor(random.random() * (100000 + 1))) +
        '&updateDate=20190315&updateDateEnd=' + time_now + '&sqlId=FW_HGT_JSHDBL',
        headers={'Referer': 'http://www.sse.com.cn/services/hkexsc/disclo/ratios/'}
    )
    #print(response.text)
    #print(response.text[19:-1])
    j = json.loads(response.text[19:-1])
    return float(j['pageHelp']['data'][0]['sellPrice'])

if __name__ == "__main__":
    #get_stock_price("SZ.300122", "2019-3-14")
    #print(get_fund_price("501018"))
    #print(get_sina_price("002027"))  #http://hq.sinajs.cn/list=sz002027
    #print(get_sina_price("160311"))  #http://hq.sinajs.cn/list=of160311
    #print(get_sina_price("831010"))  #http://hq.sinajs.cn/list=sb831010
    #print(get_sina_price("605151"))
    #print(get_sina_price("688777"))
    print(get_sina_price("300003"))
    print(get_hk_rate())
