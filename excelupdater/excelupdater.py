import openpyxl
from configparser import ConfigParser
import priceCrawler
from mathhelp.irr import xirr
import xlrd

date_now = 0

def get_headers(sheet):
    col_num = sheet.max_column
    headers = []
    for i in range(1, col_num + 1):
        headers.append(sheet.cell(row=1, column=i).value)
    return headers

def latest_price(code, exchange):
    global date_now
    if exchange in {"上海", "深圳", "香港", "新三板", "可转债", "场内基金", "新股"}:
        nav, date_now = priceCrawler.get_sina_price(code)
        return nav
    elif exchange in {"场外基金"}:
        nav, date_now = priceCrawler.get_fund_price(code)
        return nav
    elif exchange in {"现金"}:
        return 1
    else:
        return -1

def update_position_price(excelpath):
    wb = openpyxl.load_workbook(excelpath, data_only=False)

    # 更新汇率
    config_sheet = wb.get_sheet_by_name("参数")
    config_sheet.cell(row=1, column=2).value = priceCrawler.get_hk_rate()

    # 保护数据透视表格式
    pivot_sheet = wb.get_sheet_by_name("总计")
    pivot = pivot_sheet._pivots[0]  # 任何一个都可以共享同一个缓存
    pivot.cache.refreshOnLoad = True  # 刷新加载

    # 更新股价
    data_sheet = wb.get_sheet_by_name("实时持仓")
    headers = get_headers(data_sheet)
    code_col = headers.index('code') + 1
    exchange_col = headers.index('交易板块') + 1
    price_col = headers.index('股价') + 1

    row_num = data_sheet.max_row
    for i in range(2, row_num + 1):
        nav = latest_price(data_sheet.cell(i, code_col).value, data_sheet.cell(i, exchange_col).value)
        data_sheet.cell(i, price_col).value = nav
    wb.save(excelpath)

def update_stock_price(excelpath):
    wb = openpyxl.load_workbook(excelpath, data_only=False)

    # 更新汇率
    config_sheet = wb.get_sheet_by_name("参数")
    config_sheet.cell(row=1, column=2).value = priceCrawler.get_hk_rate()

    # 更新股价
    data_sheet = wb.get_sheet_by_name("当前持仓")
    headers = get_headers(data_sheet)
    code_col = headers.index('股票代码') + 1
    price_col = headers.index('现价') + 1
    inc_col = [headers.index('一日涨幅') + 1, headers.index('五日涨幅') + 1, headers.index('近一月') + 1,
                   headers.index('近半年') + 1, headers.index('近一年') + 1]

    row_num = data_sheet.max_row
    for i in range(2, row_num + 1):
        nav = latest_price(data_sheet.cell(i, code_col).value, "上海")
        data_sheet.cell(i, price_col).value = nav

        inc_list = priceCrawler.get_sina_increase(data_sheet.cell(i, code_col).value)
        if inc_list[0] != -200:
            for j in range(len(inc_col)):
                if inc_list[j] == -100:
                    data_sheet.cell(i, inc_col[j]).value = "--"
                else:
                    data_sheet.cell(i, inc_col[j]).value = inc_list[j]

    # 更新债价
    data_sheet2 = wb.get_sheet_by_name("垃圾转债")
    headers2 = get_headers(data_sheet2)
    code_col = headers2.index('股票代码') + 1
    price_col = headers2.index('现价') + 1
    rate_col = headers2.index('到期年化') + 1
    duedate_col = headers2.index('到期日期') + 1

    row_num = data_sheet2.max_row
    for i in range(2, row_num + 1):
        nav = latest_price(str(data_sheet2.cell(i, code_col).value), "上海")
        data_sheet2.cell(i, price_col).value = nav

        mytas = []
        mytas.append((date_now, - nav))
        mytas.append((data_sheet2.cell(i, duedate_col).value, 100))
        data_sheet2.cell(i, rate_col).value = xirr(mytas)
    wb.save(excelpath)

def update_hkrate(excelpath):
    wb = openpyxl.load_workbook(excelpath, data_only=False)
    sheet1 = wb.get_sheet_by_name("参数")  # 通过索引获取表格，一个文件里可能有多个sheet
    sheet1.cell(row=1, column=2).value = priceCrawler.get_hk_rate()

    # 保护数据透视表格式
    pivot_sheet = wb.get_sheet_by_name("总计")
    pivot = pivot_sheet._pivots[0]  # 任何一个都可以共享同一个缓存
    pivot.cache.refreshOnLoad = True  # 刷新加载
    wb.save(excelpath)

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('config.ini', encoding='UTF-8')
    filepath = cfg.get('file', 'position_path')
    update_position_price(filepath)
    filepath = cfg.get('file', 'stock_path')
    update_stock_price(filepath)
