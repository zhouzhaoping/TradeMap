from crawler.sina_api import *
from crawler.xueqiu_api import *
from crawler.sse_api import *
from crawler.baostock_api import *
from crawler.cache import *


def get_his_data(stockcode, date):
    #print(stockcode, date)
    # 00-深证A股，60-上证A股，300-创业板
    # 15、16、18-深证场内基金，50、51、52-上证场内基金
    # 12-深证转债，11-上证转债

    # 未上市债券
    if stockcode in {"113025", "113026", "128065"}:
        return 100.0

    try:
        if stockcode[:2] in {"60", "50", "51", "52", "00", "30", "15", "16", "18"}:
            result = get_stock_his_price(stockcode, date)
        elif stockcode == "hkrate":
            result = get_hk_his_rate(date)
        elif stockcode[:2] == "hk":
            result = get_hkstock_his_price(stockcode, date) * get_his_data("hkrate", date)
        elif stockcode[:2] == "12":
            result = get_bond_his_rate("SZ" + stockcode, date)
        elif stockcode[:2] in {"11", "13"}: #  13 for sh.EB
            result = get_bond_his_rate("SH" + stockcode, date)
        elif stockcode[:2] == "of":
            result = get_fund_his_price(stockcode, date)
        else:
            assert False, "stock error"
    except:
        print("try errororrr", stockcode, date)
        result = -1

    # for qdii 和 停牌
    if result < 0:
        print("get error", stockcode, date)
        result = get_his_data(stockcode, date - datetime.timedelta(1))
        # recache
        if stockcode[:2] == "12":
            insert_cache(("SZ" + stockcode, date), result)
        elif stockcode[:2] == "11":
            insert_cache(("SH" + stockcode, date), result)
        else:
            insert_cache((stockcode, date), result)

    return result

if __name__ == "__main__":
    #yesterday = datetime.datetime.now()-datetime.timedelta(days=2)
    #date = yesterday.date()
    # A股
    #print(get_his_data("600029", date))
    # 场内基金
    #print(get_his_data("501029", date))
    print(get_his_data("162411", datetime.datetime.strptime("2018/12/11", '%Y/%m/%d').date()))
    # 港股
    #print(get_his_data("hk00981", date))
    # 上证港股通结算汇率
    #print(get_his_data("hkrate", datetime.datetime.strptime("2019/4/19", '%Y/%m/%d').date()))
    # 场外基金
    #print(get_his_data("of110033", date))
    # qdii cannot find
    #print(get_his_data("of270042", datetime.datetime.strptime("2018-03-30", "%Y-%m-%d").date()))
    # 可转债
    #print(get_his_data("128039", date))
    # 交易日
    #print(get_his_trade_date(start_date="2018-01-27", end_date="2019-05-01"))
