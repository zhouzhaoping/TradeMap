from crawler.baostock_api import get_his_trade_date
from crawler.his_data import get_his_data
import datetime

from pyecharts import Line, Overlap

grid = [1.1, 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4]
stock_position = [0]*14
cash = 130000.0
buylevel = 10000.0
curlevel = -1

def trade(price):
    global curlevel
    if curlevel < 0:
        for i in range(len(grid)):
            grid[i] = grid[i] * price
        print("buy at", price)
        stock_position[1] = buylevel * (1 - 0.00016) / price
        curlevel = 1
    else:
        level = 0
        while price < grid[level]:
            level += 1
        if
def test():
    earn = 0.0
    trade_day = get_his_trade_date("2012-06-08", "2019-06-08")
    dates = []
    price = []
    for index, row in trade_day.iterrows():
        if row["is_trading_day"] == "0":
            continue
        curdate = datetime.datetime.strptime(row["calendar_date"], '%Y-%m-%d').date()
        curprice = get_his_data("162411", curdate, False)
        if curprice < 0:
            continue
        #print(row["calendar_date"], curprice)
        dates.append(curdate)
        price.append(curprice)
        trade(curprice)
    return dates, price


def assets_curve(dates, sum):
    xs = dates
    ys = sum

    line = Line("华宝油气走势图")
    line.add("价格", xs, sum, is_smooth=True,
             mark_line=["min", "max", "average"],
             mark_point=['min', 'max', 'average', {"coord": [xs[-1], ys[-1]], "name": "now"}],
             is_datazoom_show=True, xaxis_name="时间", yaxis_name="元", tooltip_trigger="axis")

    overlap = Overlap(width=1200, height=600)
    # 默认不新增 x y 轴，并且 x y 轴的索引都为 0
    overlap.add(line)
    overlap.render('price.html')

if __name__ == "__main__":
    dates, price = test()
    assets_curve(dates, price)
