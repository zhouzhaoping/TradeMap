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
    #print(result)
    #"乐普医疗,31.300（今开）,31.620（昨收）,31.170（今收）,31.880（今高）,30.930（今低）,31.170,31.180,21180706（成交量）,660546544.000（成交额）,16389,
    # 31.170,
    # 107500,
    # 31.160,
    # 6100,
    # 31.150,700,31.140,3800,31.130,2400,31.180,3400,31.190,20810,31.200,3100,31.210,11500,31.220,2021-03-04,15:36:00,00,D|1100|34287.000";

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
        if stock_code[:2] == "sh":
            date_now = datetime.datetime.strptime(result.split(",")[-4], '%Y-%m-%d')
        elif stock_code[:2] == "sz":
            if result.split(",")[-1].startswith("D") or result.split(",")[-1].startswith("H"): # 闭市后创业板使用这个
                date_now = datetime.datetime.strptime(result.split(",")[-4], '%Y-%m-%d')
            else:
                date_now = datetime.datetime.strptime(result.split(",")[-3], '%Y-%m-%d')
        elif stock_code[:2] == "sb":
            date_now = datetime.datetime.strptime(result.split(",")[-9], '%Y-%m-%d')
        else:
            date_now = datetime.datetime.strptime(result.split(",")[-2], '%Y/%m/%d')

        #print(stock_code, curprice, date_now)
    except:
        curprice = 100.0# todo 未上市的债券
        date_now = datetime.datetime.strptime("2021-05-01", '%Y-%m-%d')

    # 0股票名字；1今日开盘价；2昨日收盘价；3当前价格；4今日最高价；5今日最低价；6竞买价，即“买一”报价；7竞卖价，即“卖一”报价；
    # http://blog.sina.com.cn/s/blog_5dc29fcc0101dq5s.html
    #print(curprice)
    return float(curprice), date_now


def get_hk_rate():
    return 0.83502
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

# todo 合并get_sina_price接口
# 返回-200不支持；返回-100当时未上市
# 不支持场内基金、三板、转债、场外基金、香港？
def get_sina_increase(stock_code):
    url = "http://finance.sina.com.cn/realstock/company/$stock_code/qianfuquan.js"
    # 00-深证A股，60-上证A股，300-创业板
    # 15、16、18-深证场内基金，50、51、52-上证场内基金
    # 12-深证转债，11-上证转债
    if stock_code[:2] in {"60", "68"}:  # 13 for EB; 68 for 科创板
        stock_code = "sh" + stock_code
    elif stock_code[:2] in {"00", "30"}:
        stock_code = "sz" + stock_code
    else:
        return [-200, -200, -200, -200, -200]
    url = url.replace("$stock_code", stock_code)
    r = requests.get(url)
    #print(url)
    result = r.content.decode('GBK')
    #print(result)

    pricelist = result.split("\"")
    #print(pricelist)
    oneday_inc = oneweek_inc = onemonth_inc = halfyear_inc = oneyear_inc = -100
    try:
        oneday_inc = float(pricelist[1]) / float(pricelist[1 + 1*2]) * 100 - 100
        oneweek_inc = float(pricelist[1]) / float(pricelist[1 + 5*2]) * 100 - 100
        onemonth_inc = float(pricelist[1]) / float(pricelist[1 + 20*2]) * 100 - 100
        halfyear_inc = float(pricelist[1]) / float(pricelist[1 + 100*2]) * 100 - 100
        oneyear_inc = float(pricelist[1]) / float(pricelist[1 + 200*2]) * 100 - 100
    except:
        pass

    return [oneday_inc, oneweek_inc, onemonth_inc, halfyear_inc, oneyear_inc]

if __name__ == "__main__":
    #get_stock_price("SZ.300122", "2019-3-14")
    #print(get_fund_price("501018"))
    #print(get_sina_increase("000001"))
    #print(get_sina_increase("002027"))  #http://hq.sinajs.cn/list=sz002027
    #print(get_sina_increase("160311"))  #http://hq.sinajs.cn/list=of160311
    #print(get_sina_increase("831010"))  #http://hq.sinajs.cn/list=sb831010
    #print(get_sina_increase("123067"))
    #print(get_sina_increase("688981"))
    #print(get_sina_increase("832456"))
    #print(get_fund_price("006586"))
    print(get_hk_rate())
