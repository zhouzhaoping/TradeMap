from crawler.baostock_api import get_his_trade_date
from crawler.his_data import get_his_data
import datetime

def test():
    stock_position = 0.0
    earn = 0.0
    trade_day = get_his_trade_date("2012-06-08", "2019-06-08")
    for index, row in trade_day.iterrows():
        if row["is_trading_day"] == "0":
            continue
        price = get_his_data("162411", datetime.datetime.strptime(row["calendar_date"], '%Y-%m-%d').date())
        print(row["calendar_date"], price)

if __name__ == "__main__":
    test()