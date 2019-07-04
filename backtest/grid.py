from crawler.baostock_api import get_his_trade_date
from crawler.his_data import get_his_data
import datetime

from pyecharts import Line, Overlap

grid = [1.1, 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4]
#[0.9328000000000001, 0.848, 0.8056, 0.7632, 0.7208, 0.6784, 0.636, 0.5935999999999999, 0.5512, 0.5087999999999999, 0.46640000000000004, 0.424, 0.3816, 0.3392]
stock_position = [0]*14
cash = 130000.0
buylevel = 10000.0
curlevel = -1

def trade(price, datestr):
    global curlevel
    global cash
    if curlevel < 0:#initial
        for i in range(len(grid)):
            grid[i] = grid[i] * price
        print(grid)
        print(datestr)
        print("initial buy at", price, "level at 1")
        cash -= buylevel
        stock_position[1] = buylevel * (1 - 0.00016) / price
        curlevel = 1
    elif curlevel == 0 and stock_position[1] == 0.0:# Empty position
        if price <= grid[1]:
            print(datestr)
            print("initial buy at", price, "level at 1")
            cash -= buylevel
            stock_position[1] = buylevel * (1 - 0.00016) / price
            curlevel = 1
            level = 0
            while price < grid[level]:
                level += 1
            while curlevel + 1 < level:
                curlevel += 1
                print(datestr)
                print("buy at", price, "level at", curlevel)
                cash -= buylevel
                stock_position[curlevel] = buylevel * (1 - 0.00016) / price
    else:
        level = 0
        while price < grid[level]:
            level += 1
        while curlevel > 0 and curlevel > level:
            print(datestr)
            print("sell at", price, "level at", curlevel)
            cash += stock_position[curlevel] * price * (1 - 0.00016)
            stock_position[curlevel] = 0
            curlevel -= 1
        while curlevel + 1 < level:
            curlevel += 1
            print(datestr)
            print("buy at", price, "level at", curlevel)
            cash -= buylevel
            stock_position[curlevel] = buylevel * (1 - 0.00016) / price
    sum = cash
    for i in range(len(stock_position)):
        sum += stock_position[i] * price
    return sum

def test():
    assets = []
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
        assets.append(trade(curprice, row["calendar_date"]))
        #print(row["calendar_date"], assets[-1])
    return dates, price


def assets_curve(dates, sum):
    xs = dates
    ys = sum

    line = Line("华宝油气走势图")
    line.add("价格", xs, sum, is_smooth=True,
             mark_line=["min", "max", "average"],
             mark_point=['min', 'max', 'average', {"coord": [xs[-1], ys[-1]], "name": "now"}],
             is_datazoom_show=True, xaxis_name="时间", yaxis_name="元", tooltip_trigger="axis")
    #todo 买卖点，收益曲线
    overlap = Overlap(width=1200, height=600)
    # 默认不新增 x y 轴，并且 x y 轴的索引都为 0
    overlap.add(line)
    overlap.render('price.html')

if __name__ == "__main__":
    dates, price = test()
    assets_curve(dates, price)
