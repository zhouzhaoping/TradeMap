from crawler.baostock_api import get_his_trade_date
from crawler.rim_api import get_rimvalue_top100, RimValue
from crawler.baostock_api import get_his_trade_date_firstday
import datetime
from backtest.BuyList import *
from crawler.his_data import get_his_data


def gen_buy_list(trade_days, candidateLen=5):
    buyLists = []
    for d in trade_days:
        buyList = BuyList(d)
        top100 = get_rimvalue_top100(d - datetime.timedelta(days=1))
        for i in range(0, candidateLen):
            rimvalue = RimValue()
            rimvalue.dump(top100[i])
            buyList.add(rimvalue.code[:6])
        buyLists.append(buyList)
    return buyLists


def rim_test(buyLists):
    candidateLen = len(buyLists[0].codes)

    money = 100000.0
    stock = list(range(candidateLen))

    for list_i in range(len(buyLists)):
       if list_i != 0:
           money = 0.0
           for candidate_i in range(candidateLen):
               money += stock[candidate_i] * get_his_data(buyLists[list_i - 1].codes[candidate_i], buyLists[list_i].date)
               print(buyLists[list_i].date, money)
       for candidate_i in range(candidateLen):
           stock[candidate_i] = money / candidateLen


if __name__ == "__main__":
    trade_days = get_his_trade_date_firstday("2016-01-01", "2019-11-01")
    buyLists = gen_buy_list(trade_days)
    rim_test(buyLists)

