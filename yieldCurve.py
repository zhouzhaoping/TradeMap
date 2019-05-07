from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import excelReader
import pandas as pd
import numpy as np
from datetime import date
from pylab import *
import priceCrawler
from IPython.display import display
import datetime
from pyecharts import Line, Overlap

def xirr(transactions):
    years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
    residual = 1
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, ta in enumerate(transactions):
            residual += ta[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess - 1


def stock_irr(stock_code, tas):
    mytas = []
    for (code, record_date, cost) in tas:
        if stock_code == "all" or code == stock_code:
            mytas.append((record_date, cost))
    try:
        return xirr(mytas) * 100
    except:
        print("irr error: stock_code=", stock_code)
        return -100.0

def bet2cost(interest_days):
    cost = [interest_days*10, 7000, 2900, 3879.6, 24000, 33000]
    name = ["利息", "世界杯入市", "电动车", "显示器", "东王庄房租", "展春园房租"]
    ret = []
    sum = 0.0
    for i in range(len(cost)):
        sum += cost[i]
        ret.append({"name": name[i], "yAxis": sum})
    return ret

def bet():
    dates, profits = excelReader.get_bet_data()

    xs = dates
    ys = profits
    xs_delta = [(x - min(xs)).days + 1 for x in xs]
    xs_date = [x.date() for x in xs]
    ys_perday = [round(y / x, 2) for (y, x) in zip(ys, xs_delta)]

    line1 = Line("日均盈利走势图")
    line1.add("日均盈利", xs_date, ys_perday, is_smooth=True,
             mark_line=["min", "max", "average"],
             mark_point=['min', 'max', 'average', {"coord": [xs_date[-1], ys_perday[-1]], "name": "now"}],
             is_datazoom_show=True, xaxis_name="时间", yaxis_name="元", tooltip_trigger="axis")

    line2 = Line("日均盈利走势图")
    line2.add("总盈亏", xs_date, ys, is_smooth=True,
              mark_line_raw=bet2cost(xs_delta[-1]),
              is_datazoom_show=True, xaxis_name="时间", yaxis_name="元", tooltip_trigger="axis",is_yaxis_show=False)

    overlap = Overlap(width=1200, height=600)
    # 默认不新增 x y 轴，并且 x y 轴的索引都为 0
    overlap.add(line1)
    # 新增一个 y 轴，此时 y 轴的数量为 2，第二个 y 轴的索引为 1（索引从 0 开始），所以设置 yaxis_index = 1
    # 由于使用的是同一个 x 轴，所以 x 轴部分不用做出改变
    overlap.add(line2, yaxis_index=1, is_add_yaxis=True)
    overlap.render('bet.html')

def stock():
    code2stock_summary, tas = excelReader.check_stock_data()

    date_now = ""
    data = {'code': [], 'stock': [], 'position': [], 'nav': [], 'profit': [], 'rate%': [], 'irr_rate%': []}
    for stock_code in code2stock_summary.keys():
        nav, date_now = priceCrawler.get_sina_price(stock_code)
        if stock_code[:2] == "hk":
            nav = nav * priceCrawler.get_hk_rate()

        code2stock_summary[stock_code].rate(nav)
        tas.append((stock_code, date_now, code2stock_summary[stock_code].value))
        data['code'].append(stock_code)
        data['stock'].append(code2stock_summary[stock_code].name)
        data['position'].append(code2stock_summary[stock_code].position)
        data['nav'].append(nav)
        data['profit'].append(round(code2stock_summary[stock_code].profit,2))
        data['rate%'].append(round(code2stock_summary[stock_code].rate,2))
        data['irr_rate%'].append(round(stock_irr(stock_code, tas), 2))

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', None)
    df = pd.DataFrame(data)
    df = df.sort_values(by='irr_rate%', ascending=False)

    #显示所有列
    pd.set_option('display.max_columns', None)
    #显示所有行
    pd.set_option('display.max_rows', None)
    print(df)
    df.to_csv("stock.csv", index=False)

    print(date_now.date(), "irr_rate_all", round(stock_irr("all", tas),2))
    return


def fund():
    code2stock_summary, tas = excelReader.get_fund_data()

    date_now = ""
    data = {'code': [], 'stock': [], 'position': [], 'nav': [], 'profit': [], 'rate%': [], 'irr_rate%': []}
    for stock_code in code2stock_summary.keys():
        nav, date_now = priceCrawler.get_fund_price(stock_code)
        code2stock_summary[stock_code].rate(nav)
        tas.append((stock_code, date_now, code2stock_summary[stock_code].value))
        #code2stock_summary[stock_code].print()
        data['code'].append(stock_code)
        data['stock'].append(code2stock_summary[stock_code].name)
        data['position'].append(code2stock_summary[stock_code].position)
        data['nav'].append(code2stock_summary[stock_code].position)
        data['profit'].append(round(code2stock_summary[stock_code].profit, 2))
        data['rate%'].append(round(code2stock_summary[stock_code].rate, 2))
        data['irr_rate%'].append(round(stock_irr(stock_code, tas), 2))

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', None)
    df = pd.DataFrame(data)
    df = df.sort_values(by='irr_rate%', ascending=False)

    #显示所有列
    pd.set_option('display.max_columns', None)
    #显示所有行
    pd.set_option('display.max_rows', None)
    print(df)
    df.to_csv("fund.csv", index=False)

    print(date_now.date(), "irr_rate_all", round(stock_irr("all", tas), 2))
    return


if __name__ == "__main__":
    bet()
    #stock()
    #fund()
    #todo 总irr计算，不同时间投入的总资金，货币基金按照每日万一计算，
    #tas = [(date(2010, 12, 29), -10000),
    #       (date(2012, 1, 25), 20),
    #       (date(2012, 3, 8), 10100)]
    #print(xirr(tas))  # 0.0100612640381
