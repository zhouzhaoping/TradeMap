import xlrd
from datetime import datetime
from StockSummary import StockSummary
from configparser import ConfigParser
from curve.Assets import *


def get_table_from_file(table_name):
    cfg = ConfigParser()
    cfg.read('config.ini', encoding='UTF-8')
    filepath = cfg.get('file', 'path')
    data = xlrd.open_workbook(filepath)
    table = data.sheet_by_name(table_name)
    return table


def get_row_by_name(table, name, taildel):
    headers = table.row_values(0)
    index = headers.index(name)
    ctype = table.cell_type(1, index)
    # ctype： 0 empty, 1 string, 2 number, 3 date, 4 boolean, 5 error

    #print(table.nrows, name, ctype)
    result = list()
    for line in range(1, table.nrows - taildel):
        if ctype == 1:
            result.append(table.cell(line, index).value)
        elif ctype == 2:
            result.append(round(table.cell(line, index).value, 2))
        elif ctype == 3:
            result.append(xlrd.xldate.xldate_as_datetime(table.cell(line, index).value, 0))
    return result


def get_bet_data():
    table = get_table_from_file('赌球')
    return get_row_by_name(table, '日期', True), get_row_by_name(table, '阶段性盈利', True)


def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]


def round_up(value):
    # 替换内置round函数,实现保留2位小数的精确四舍五入
    return round(value + 0.00001, 2)


def check_stock_data():
    table = get_table_from_file('场内交割单')
    headers = table.row_values(0)
    code_index = headers.index('股票代码')
    name_index = headers.index('股票名称')
    code2name = {}
    code2stock_summary = {}
    tas = []  # tas = [(code, date(2010, 12, 29), -10000),

    for line in range(1, table.nrows):
        # 检查股票代码和名字一一对应
        code = table.cell(line, code_index).value
        name = table.cell(line, name_index).value
        if code in code2name:
            assert name == code2name[code], "stock name and code conflict"
        elif name in code2name.values():
            assert code == get_key(code2name, name), "stock name and code conflict" + str(line) + " " + code
        else:
            code2name[code] = name
            code2stock_summary[code] = StockSummary(name, 0, 0.0, 0.0)

        # 检查总仓位
        buy_type = table.cell(line, headers.index('买卖方向')).value
        if buy_type == "买入":
            code2stock_summary[code].add(int(table.cell(line, headers.index('成交数量')).value),
                                         -table.cell(line, headers.index('发生金额')).value, 0.0)
        elif buy_type == "卖出":
            code2stock_summary[code].add(int(table.cell(line, headers.index('成交数量')).value), 0.0,
                                         table.cell(line, headers.index('发生金额')).value)
        elif buy_type == "中签":
            code2stock_summary[code].add(int(table.cell(line, headers.index('成交数量')).value),
                                         -table.cell(line, headers.index('发生金额')).value, 0.0)
        elif buy_type == "分红" or buy_type == "股息":
            code2stock_summary[code].add(0, 0.0, table.cell(line, headers.index('发生金额')).value)
            assert code2stock_summary[code].position == -table.cell(line, headers.index('成交数量')).value, "分红数量有误"+str(line)
        elif buy_type == "红利补缴":
            code2stock_summary[code].add(0, 0.0, table.cell(line, headers.index('发生金额')).value)
        elif buy_type == "送股":
            code2stock_summary[code].add(
                int(table.cell(line, headers.index('成交数量')).value), 0.0, 0.0)
        else:
            assert False, "stock buy_type error"

        # 00-深证A股，60-上证A股，300-创业板
        # 15、16、18-深证场内基金，50、51、52-上证场内基金
        # 12-深证转债，11-上证转债
        # 检查手续费
        if line <= 1: # todo 不检查
            volume = table.cell(line, headers.index('成交金额')).value
            commission = round_up(abs(volume) * 0.00016)
            stamp_tax = 0.0
            other = round_up(abs(volume) * 0.00002)
            if code[:2] in {"00"} and line > 416: # 光大不收深证
                other = 0.0
            if buy_type == "分红" or buy_type == "股息" or buy_type == "中签" or table.cell(line, headers.index('委托号')).value == 5397:#平银转债债转股
                commission = other = 0.0
            else:
                if code[:2] == "hk":
                    # TODO need to check
                    commission = table.cell(line, headers.index('手续费')).value
                    stamp_tax = table.cell(line, headers.index('印花税')).value
                    other = table.cell(line, headers.index('其他杂费')).value
                elif code[:2] in {"00", "60", "30"}:
                    if commission < 5.0:
                        commission = 5.0
                    if buy_type == "卖出":
                        stamp_tax = round_up(abs(volume) * 0.001)
                elif code[:2] in {"15", "16", "18", "50", "51", "52"}:
                    if commission < 0.1:
                        commission = 0.1
                    other = 0
                elif code[:2] in {"11", "12"}:
                    if code[:2] == "12":
                        commission = round_up(abs(volume) * 0.0001)
                    else:
                        commission = round_up(abs(volume) * 0.0002)
                        if commission < 1.0:
                            commission = 1.0
                    other = 0
                else:
                    assert False, "stock code error"
            if table.cell(line, headers.index('说明')).value != '光大周彦伶':
                assert table.cell(line, headers.index('手续费')).value == commission, "股票手续费错误"+ str(line)
            if buy_type != "股息":
                assert table.cell(line, headers.index('印花税')).value == stamp_tax, "股票印花税错误"
            if table.cell(line, headers.index('委托号')).value != 25037:
                assert table.cell(line, headers.index('其他杂费')).value == other, str(other) +  "股票其它杂费错误" + str(table.cell(
                    line,
                                                                                                           headers.index('委托号')).value)

            # 计算年化率
        tas.append((code, xlrd.xldate.xldate_as_datetime(table.cell(line, headers.index('时间')).value, 0),
                    table.cell(line, headers.index('发生金额')).value))
    return code2stock_summary, tas


def get_fund_data():
    table = get_table_from_file('场外基金')
    headers = table.row_values(0)
    code_index = headers.index('代码')
    name_index = headers.index('基金名称')
    code2name = {}
    code2stock_summary = {}
    tas = []  # tas = [(code, date(2010, 12, 29), -10000),

    for line in range(1, table.nrows):
        # 检查基金代码和名字一一对应
        code = table.cell(line, code_index).value
        name = table.cell(line, name_index).value
        if code in code2name:
            assert name == code2name[code], "stock name and code conflict"
        elif name in code2name.values():
            assert code == get_key(code2name, name), "stock name and code conflict"
        else:
            code2name[code] = name
            code2stock_summary[code] = StockSummary(name, 0, 0.0, 0.0)

        # 检查总仓位
        buy_type = table.cell(line, headers.index('操作')).value
        if buy_type == "买入":
            code2stock_summary[code].add(table.cell(line, headers.index('份额')).value,
                                         -table.cell(line, headers.index('总额')).value, 0.0)
        elif buy_type == "卖出":
            code2stock_summary[code].add(table.cell(line, headers.index('份额')).value, 0.0,
                                         table.cell(line, headers.index('总额')).value)
        elif buy_type in {"分红", "股息"}:
            code2stock_summary[code].add(table.cell(line, headers.index('份额')).value, 0.0,
                                         table.cell(line, headers.index('总额')).value)
        else:
            assert False, "stock buy_type error"

        # 计算年化率
        tas.append((code, xlrd.xldate.xldate_as_datetime(table.cell(line, headers.index('时间')).value, 0),
                    table.cell(line, headers.index('总计')).value))
    return code2stock_summary, tas

def get_all_flow():
    flows = list()
    table = get_table_from_file('场内交割单')
    stock_trade = zip(get_row_by_name(table, '时间', False), get_row_by_name(table, '买卖方向', False), get_row_by_name(table, '股票代码', False), get_row_by_name(table, '成交数量', False), get_row_by_name(table, '发生金额', False))
    for (time, type, code, position, flow) in stock_trade:
        if type == "分红" or type == "股息": #todo 分红只考虑分现金，不考虑拆股
            position = 0
        flows.append(Flow(time, code, position, flow))

    table = get_table_from_file('场外基金')
    stock_trade = zip(get_row_by_name(table, '时间', False), get_row_by_name(table, '操作', False), get_row_by_name(table, '代码', False), get_row_by_name(table, '份额', False), get_row_by_name(table, '总额', False))
    for (time, type, code, position, flow) in stock_trade:
        flows.append(Flow(time, "of" + code, position, flow))

    flowSort(flows)
    #for flow in flows:
    #    print(flow.time, flow.code, flow.position, flow.flow)
    return flows

if __name__ == "__main__":
    #check_stock_data()
    #get_fund_data()
    flows = get_all_flow()


