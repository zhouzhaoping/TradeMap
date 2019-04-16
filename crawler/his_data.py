from crawler.sina_api import *
from crawler.xueqiu_api import *
from crawler.sse_api import *


def get_his_data(stockcode, date):
    # 00-深证A股，60-上证A股，300-创业板
    # 15、16、18-深证场内基金，50、51、52-上证场内基金
    # 12-深证转债，11-上证转债
    if stockcode[:2] in {"60", "50", "51", "52", "00", "30", "15", "16", "18"}:
        return get_stock_his_price(stockcode, date)
    elif stockcode[:2] == "hk":
        return get_hkstock_his_price(stockcode, date) * get_hk_his_rate(date)
    elif stockcode[:2] == "12":
        return get_bond_his_rate("SZ" + stockcode, date)
    elif stockcode[:2] == "11":
        return get_bond_his_rate("SH" + stockcode, date)
    elif stockcode[:2] == "of":
        return get_fund_his_price(stockcode, date)


if __name__ == "__main__":
    yesterday = datetime.datetime.now()-datetime.timedelta(days=2)
    date = yesterday.date()
    # A股
    print(get_his_data("600029", date))
    # 场内基金
    print(get_his_data("501029", date))
    # 港股
    print(get_his_data("hk00981", date))
    # 场外基金
    print(get_his_data("of110033", date))
    # 可转债
    print(get_his_data("128039", date))
