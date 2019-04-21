import pandas_datareader.data as web
import datetime

start = datetime.datetime(2017, 1, 1)#获取数据的时间段-起始时间
end = datetime.date.today()#获取数据的时间段-结束时间
stock = web.DataReader("600797.SS", "yahoo", start, end)#获取浙大网新2017年1月1日至今的股票数据
print(stock)