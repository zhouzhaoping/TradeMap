



# 可转债
# https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ128040&begin=1555517900000&period=day&count=-1
def get_bond_his_rate(date, ifcache=True):
    dict = cache.get_cache()
    if ifcache and ("hkrate", date) in dict.keys():
        print("hit")
        return dict[("hkrate", date)]

    datestr = date.strftime("%Y%m%d")
    # print(datestr)
    response = requests.get(
        'http://query.sse.com.cn/commonSoaQuery.do?&jsonCallBack=jsonpCallback'
        + str(math.floor(random.random() * (100000 + 1))) +
        '&updateDate=' + datestr + '&updateDateEnd=' + datestr + '&sqlId=FW_HGT_JSHDBL',
        headers={'Referer': 'http://www.sse.com.cn/services/hkexsc/disclo/ratios/'}
    )
    # print(response.text)
    j = json.loads(response.text[19:-1])
    rate = float(j['result'][0]['sellPrice'])

    print("insert", date, rate)
    dict["hkrate", date] = rate
    cache.save_cache(dict)
    if ("hkrate", date) in dict.keys():
        return dict["hkrate", date]
    else:
        return -1


if __name__ == "__main__":
    # 上证港股通结算汇率
    print(get_hk_his_rate(datetime.datetime.strptime("2019/4/9", '%Y/%m/%d').date()))
