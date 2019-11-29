from crawler.baostock_api import get_his_trade_date
from crawler.rim_api import get_rimvalue_top100, RimValue
from crawler.baostock_api import get_his_trade_date_firstday, get_his_trade_date_firstday_of_week
import datetime
from backtest.BuyList import *
from crawler.baostock_api import get_stock_his_price, his_hs300
from crawler.cache import print_cache_all

# 共识：沪深300，每月调仓；100左右的时候大概能选出30只股票

# 无加权
# 10 - 106249.2595360303
# 20 - 104686.83130543599
# 100 - 103793.31021320228

# 因子加权
# 10 - 102710.20039949297
# 20 - 103461.43789267815
# 100 - 103020.61656024429

# 因子平均值控制仓位 + 无加权
# 10 - 106030.68946882138
# 20 - 107216.61528397526
# 100 - 107375.15068153891

# 因子平均值控制仓位 + 加权
# 10 - 102562.00909803095
# 20 - 105935.04614079969
# 100 - 106580.04864030385

# 每周调仓 + 无加权
# 10 - 109195.57401746849
# 20 - 111461.22717042704
# 100 - 106752.30352452073

# 因子筛选？2？；用大集合的平均因子变动来控制仓位？


def gen_buy_list(trade_days, candidateLen=20):
    buyLists = []
    for d in trade_days:
        buyList = BuyList(d)
        top100 = get_rimvalue_top100(d - datetime.timedelta(days=1))
        hs300 = his_hs300(d - datetime.timedelta(days=1))
        count = 0
        for i in range(100):
            rimvalue = RimValue()
            rimvalue.dump(top100[i])
            if rimvalue.code in hs300:
                buyList.add(rimvalue.code, rimvalue.name, rimvalue.vp)
                count += 1
                if count >= candidateLen:
                    break
        buyList.countPosition()
        buyLists.append(buyList)
    return buyLists


def rim_test(buyLists):

    money = 100000.0
    stock = list(range(100))

    for list_i in range(len(buyLists)):
        if list_i != 0:
            for candidate_i in range(len(buyLists[list_i-1].codes)):#卖掉
                money += stock[candidate_i] * float(get_stock_his_price(buyLists[list_i - 1].codes[candidate_i], buyLists[list_i].date))
                print("sell", buyLists[list_i - 1].rates[candidate_i], buyLists[list_i - 1].names[candidate_i], get_stock_his_price(buyLists[list_i - 1].codes[candidate_i], buyLists[list_i-1].date), get_stock_his_price(buyLists[list_i - 1].codes[candidate_i], buyLists[list_i].date))
            print(buyLists[list_i].date, money)
        for candidate_i in range(len(buyLists[list_i].codes)):# 买入
            stock[candidate_i] = money / len(buyLists[list_i].rates) / \
                                 float(get_stock_his_price(buyLists[list_i].codes[candidate_i], buyLists[list_i].date))
            #stock[candidate_i] = money * buyLists[list_i].position / buyLists[list_i].ratesum * buyLists[
        # list_i].rates[candidate_i] / float(get_stock_his_price(buyLists[list_i].codes[candidate_i], buyLists[list_i].date))
        #money = money * (1 - buyLists[list_i].position)
        money = money * 0

if __name__ == "__main__":
    #print(his_hs300(datetime.datetime.strptime("2018-09-03", '%Y-%m-%d').date()))
    #buyLists = gen_buy_list([datetime.datetime.strptime("2018-09-03", '%Y-%m-%d').date()], 101)
    trade_days = get_his_trade_date_firstday_of_week("2016-01-01", "2019-11-01")
    buyLists = gen_buy_list(trade_days, 101)
    rim_test(buyLists)

