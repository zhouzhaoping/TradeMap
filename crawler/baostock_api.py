import baostock as bs
import pandas as pd

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
