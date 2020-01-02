import baostock as bs
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from crawler.cache import get_cache, save_cache
from crawler.Kdata import Kdata, SessionCls

# 获取交易日
def get_his_trade_date(start_date="2018-01-27", end_date="2019-05-01"):
    #### 登陆系统 ####
    lg = bs.login(user_id="anonymous", password="123456")
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    #### 获取交易日信息 ####
    rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)
    print('query_trade_dates respond error_code:'+rs.error_code)
    print('query_trade_dates respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 登出系统 ####
    bs.logout()

    #### 结果集输出到csv文件 ####
    #result.to_csv("/data/trade_datas.csv", encoding="gbk", index=False)
    return result


def get_his_trade_date_clear(start_date="2018-01-27", end_date="2019-05-01"):
    result = get_his_trade_date(start_date, end_date)
    trade_days = []
    for index, row in result.iterrows():
        if row["is_trading_day"] == "1":
            trade_days.append(datetime.datetime.strptime(row["calendar_date"], '%Y-%m-%d').date())
    return trade_days


def get_his_trade_date_firstday(start_date="2018-01-27", end_date="2019-05-01"):
    result = get_his_trade_date_clear(start_date, end_date)
    year = result[0].year
    month = result[0].month
    firstDay = datetime.date(year, month, day=1)
    trade_days = []
    while firstDay <= datetime.datetime.strptime(end_date, '%Y-%m-%d').date():
        if firstDay in result:
            trade_days.append(firstDay)
            firstDay = firstDay.replace(day=1) + relativedelta(months=1)
        else:
            firstDay += datetime.timedelta(days=1)
    return trade_days


def get_his_trade_date_firstday_of_week(start_date="2018-01-27", end_date="2019-05-01"):
    result = get_his_trade_date_clear(start_date, end_date)
    trade_days = []
    for day in result:
        if day.weekday() == 0:
            trade_days.append(day)
    return trade_days


def get_stock_his_price(stockcode, date):
    #创建与数据库的会话session class
    #注意,这里返回给session的是个class,不是实例
    session = SessionCls()
    k = session.query(Kdata).filter_by(date=date, code=stockcode).first()
    if k is not None:
        return k.close

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    #print('login respond error_code:'+lg.error_code)
    #print('login respond  error_msg:'+lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    rs = bs.query_history_k_data_plus(stockcode,
                                      "date,close",
                                      start_date=datetime.date(date.year, 1, 1).strftime('%Y-%m-%d'),
                                      end_date=datetime.date(date.year, 12, 31).strftime('%Y-%m-%d'),
                                      frequency="d", adjustflag="3")
    #print('query_history_k_data_plus respond error_code:'+rs.error_code)
    #print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    result = -1.0
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data = rs.get_row_data()
        data_list.append(Kdata(date=data[0], code=stockcode, close=data[1]))
        if date == data[0]:
            result = data[1]

    #result = pd.DataFrame(data_list, columns=rs.fields)



    #可以添加多个字段
    session.add_all(data_list)
    #修改字段名字,只要没提交,此时修改也没问题
    #h2.hostname = 'ubuntu_test'
    #支持数据回滚
    #session.rollback()
    #提交
    session.commit()

    #### 结果集输出到csv文件 ####
    #print(result)

    #### 登出系统 ####
    bs.logout()

    return result

def his_hs300(date, ifcache = True):
    dict = get_cache()
    if ifcache and ("hs300", date) in dict.keys():
        #print("hit")
        return dict["hs300", date]

    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    #print('login respond error_code:'+lg.error_code)
    #print('login respond  error_msg:'+lg.error_msg)

    # 获取沪深300成分股
    rs = bs.query_hs300_stocks(str(date))
    #print('query_hs300 error_code:'+rs.error_code)
    #print('query_hs300  error_msg:'+rs.error_msg)

    # 打印结果集
    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    result = pd.DataFrame(hs300_stocks, columns=rs.fields)
    # 结果集输出到csv文件
    #print(result)
    datas = []
    for data in hs300_stocks:
        datas.append(data[1])

    if ifcache:
        dict["hs300", date] = datas
        save_cache(dict)

    # 登出系统
    bs.logout()
    return datas

if __name__ == "__main__":
    #trade_days = get_his_trade_date_clear()
    #print(trade_days[0], type(trade_days[0]))
    #print(get_his_trade_date_firstday())
    #print(get_stock_his_price("sh.600000", datetime.datetime.strptime("2019-06-06", '%Y-%m-%d').date()))
    #print(get_stock_his_price("sh.600000", datetime.datetime.strptime("2020-01-01", '%Y-%m-%d').date()))
    #print(get_stock_his_price("sz.002936", datetime.datetime.strptime("2018-09-19", '%Y-%m-%d').date()))
    print(get_stock_his_price("sh.501050", datetime.datetime.strptime("2019-09-19", '%Y-%m-%d').date()))
    #print(his_hs300(datetime.datetime.strptime("2018-09-03", '%Y-%m-%d').date()))
    #print(get_his_trade_date_firstday_of_week())
