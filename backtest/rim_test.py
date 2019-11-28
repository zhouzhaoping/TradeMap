from crawler.baostock_api import get_his_trade_date
from crawler.rim_api import get_rimvalue_top100, RimValue
from crawler.baostock_api import get_his_trade_date_firstday
import datetime
from backtest.BuyList import *
from crawler.baostock_api import get_stock_his_price, his_hs300

# 共识：沪深300；100左右的时候大概能选出30只股票

# 无加权
# 10 - 106249.2595360303
# 20 - 104686.83130543599
# 100 - 103793.31021320228

# 因子加权
# 10 - 102710.20039949297
# 20 - 103461.43789267815
# 100 - 103020.61656024429

# 因子平均值控制仓位 + 加权
# 10 - 102562.00909803095
# 20 - 105935.04614079969
# 100 - 106580.04864030385

# 因子筛选？2？；用大集合的平均因子变动来控制仓位？
# 每周调仓

def gen_buy_list(trade_days, candidateLen=20):
    buyLists = []
    for d in trade_days:
        buyList = BuyList(d)
        top100 = get_rimvalue_top100(d - datetime.timedelta(days=1))
        hs300 = his_hs300(d)
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
        print(buyList)
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
            stock[candidate_i] = money * buyLists[list_i].position / buyLists[list_i].ratesum * buyLists[list_i].rates[candidate_i] / float(get_stock_his_price(buyLists[list_i].codes[candidate_i], buyLists[list_i].date))
        money = money * (1 - buyLists[list_i].position)

if __name__ == "__main__":
    trade_days = get_his_trade_date_firstday("2016-01-01", "2019-11-01")
    buyLists = gen_buy_list(trade_days, 101)
    rim_test(buyLists)

