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

def bet():
    dates, profits = excelReader.get_bet_data()

    xs = dates
    ys = profits
    xs_delta = [(x - min(xs)).days + 1 for x in xs]
    ys_perday = [round(y / x, 2) for (y, x) in zip(ys, xs_delta)]

    # 中文显示
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # 配置横坐标
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xlabel(r'时间')

    # 配置纵坐标
    plt.yticks(np.arange(round(min(ys) / 5000)*5000, round(max(ys) / 5000)*5000+1, 5000.0))
    plt.ylabel(r'总盈亏：元', color='b')

    # Plot
    plt.plot(xs, ys, 'b-')
    plt.gcf().autofmt_xdate()  # 自动旋转日期标记

    # max and min
    max_index = ys.index(max(ys))
    min_index = ys.index(min(ys))
    plt.scatter(xs[max_index], ys[max_index], marker='o', c='r')
    plt.text(xs[max_index], ys[max_index], s=str(ys[max_index]))
    plt.scatter(xs[min_index], ys[min_index], marker='o', c='g')
    plt.text(xs[min_index], ys[min_index], s=str(ys[min_index]))

    # now
    plt.scatter(xs[-1], ys[-1], marker='*')
    plt.text(xs[-1], ys[-1], s=str(ys[-1]))

    # irr data
    plt.twinx()
    plt.plot(xs, ys_perday, 'r-')
    plt.ylabel(r'日均盈利：元', color='r')

    # max and min
    max_index = ys_perday.index(max(ys_perday))
    min_index = ys_perday.index(min(ys_perday))
    plt.scatter(xs[max_index], ys_perday[max_index], marker='o', c='r')
    plt.text(xs[max_index], ys_perday[max_index], s=str(round(ys_perday[max_index], 2)))
    plt.scatter(xs[min_index], ys_perday[min_index], marker='o', c='g')
    plt.text(xs[min_index], ys_perday[min_index], s=str(round(ys_perday[min_index], 2)))

    # now
    plt.scatter(xs[-1], ys_perday[-1], marker='*')
    plt.text(xs[-1], ys_perday[-1], s=str(round(ys_perday[-1], 2)))
    plt.yticks(np.arange(round(min(ys_perday) / 20) * 20, round(max(ys_perday) / 20) * 20 + 1, 40.0))
    plt.grid(True, axis='y', linestyle="--")

    plt.show()
    return


def stock():
    code2stock_summary, tas = excelReader.check_stock_data()

    date_now = ""
    data = {'code': [], 'stock': [], 'position': [], 'profit': [], 'rate%': [], 'irr_rate%': []}
    for stock_code in code2stock_summary.keys():
        nav, date_now = priceCrawler.get_sina_price(stock_code)
        if stock_code[:2] == "hk":
            nav = nav * priceCrawler.get_hk_rate()
        code2stock_summary[stock_code].rate(nav)
        tas.append((stock_code, date_now, code2stock_summary[stock_code].value))
        data['code'].append(stock_code)
        data['stock'].append(code2stock_summary[stock_code].name)
        data['position'].append(code2stock_summary[stock_code].position)
        data['profit'].append(round(code2stock_summary[stock_code].profit,2))
        data['rate%'].append(round(code2stock_summary[stock_code].rate,2))
        data['irr_rate%'].append(round(stock_irr(stock_code, tas), 2))

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', None)
    df = pd.DataFrame(data)
    df = df.sort_values(by='irr_rate%', ascending=False)
    print(df)

    print(date_now.date(), "irr_rate_all", round(stock_irr("all", tas),2))
    return


def fund():
    code2stock_summary, tas = excelReader.get_fund_data()

    date_now = ""
    data = {'code': [], 'stock': [], 'position': [], 'profit': [], 'rate%': [], 'irr_rate%': []}
    for stock_code in code2stock_summary.keys():
        nav, date_now = priceCrawler.get_fund_price(stock_code)
        code2stock_summary[stock_code].rate(nav)
        tas.append((stock_code, date_now, code2stock_summary[stock_code].value))
        #code2stock_summary[stock_code].print()
        data['code'].append(stock_code)
        data['stock'].append(code2stock_summary[stock_code].name)
        data['position'].append(code2stock_summary[stock_code].position)
        data['profit'].append(round(code2stock_summary[stock_code].profit, 2))
        data['rate%'].append(round(code2stock_summary[stock_code].rate, 2))
        data['irr_rate%'].append(round(stock_irr(stock_code, tas), 2))

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', None)
    df = pd.DataFrame(data)
    df = df.sort_values(by='irr_rate%', ascending=False)

    print(df)
    print(date_now.date(), "irr_rate_all", round(stock_irr("all", tas), 2))
    return


if __name__ == "__main__":
    bet()
    stock()
    fund()
    #tas = [(date(2010, 12, 29), -10000),
    #       (date(2012, 1, 25), 20),
    #       (date(2012, 3, 8), 10100)]
    #print(xirr(tas))  # 0.0100612640381
