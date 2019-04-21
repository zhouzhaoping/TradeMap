from excelReader import get_all_flow
from crawler.baostock_api import get_his_trade_date
import datetime
from curve.Assets import *

from pyecharts import Line, Overlap

def gen_assets_bydate():
    flows = get_all_flow()
    #flows = flowsfuck[-50:]
    time_begin = flows[0].time.strftime('%Y-%m-%d')
    time_end = flows[-1].time.strftime('%Y-%m-%d')
    trade_day = get_his_trade_date(time_begin, time_end)
    #print(trade_day)

    trade_days = []
    assets_sum = []
    flow_index = 0
    assetsSummary = AssetsSummary()
    for index, row in trade_day.iterrows():
        if row["is_trading_day"] == "0":
            continue
        cur_trade_day = datetime.datetime.strptime(row["calendar_date"], '%Y-%m-%d')
        while flow_index < len(flows) and flows[flow_index].time <= cur_trade_day:
            assetsSummary.change_position(flows[flow_index])
            flow_index += 1
        trade_days.append(cur_trade_day)
        assets_sum.append(assetsSummary.sum(cur_trade_day.date()))
        print(cur_trade_day, assetsSummary.sum(cur_trade_day.date()))
    return trade_days, assets_sum

def assets_curve(dates, sum):
    xs = dates
    ys = sum
    xs_date = [x.date() for x in xs]

    line = Line("盈利走势图")
    line.add("盈利", xs_date, sum, is_smooth=True,
              mark_line=["min", "max", "average"], mark_point=['min', 'max', 'average', {"coord": [xs_date[-1], ys[-1]], "name": "now"}],
              is_datazoom_show=True, xaxis_name="时间", yaxis_name="元", tooltip_trigger="axis")


    overlap = Overlap(width=1200, height=600)
    # 默认不新增 x y 轴，并且 x y 轴的索引都为 0
    overlap.add(line)
    overlap.render('profit.html')

if __name__ == "__main__":
    trade_days, assets_sum = gen_assets_bydate()
    assets_curve(trade_days, assets_sum)