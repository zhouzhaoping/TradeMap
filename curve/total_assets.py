from excelReader import get_all_flow
from crawler.baostock_api import get_his_trade_date
import datetime
from curve.Assets import *

def gen_assets_bydate():
    flows = get_all_flow()
    time_begin = flows[0].time.strftime('%Y-%m-%d')
    time_end = flows[-1].time.strftime('%Y-%m-%d')
    trade_day = get_his_trade_date(time_begin, time_end)

    flow_index = 0
    assetsSummary = AssetsSummary()
    for index, row in trade_day.iterrows():
        if row["is_trading_day"] == "0":
            continue
        cur_trade_day = datetime.datetime.strptime(row["calendar_date"], '%Y-%m-%d')
        while flows[flow_index].time <= cur_trade_day:
            assetsSummary.change_position(flows[flow_index])
            flow_index += 1
        print(cur_trade_day, assetsSummary.sum(cur_trade_day.date()))

if __name__ == "__main__":
    gen_assets_bydate()