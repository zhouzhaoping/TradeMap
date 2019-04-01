import xlrd
from datetime import datetime
from StockSummary import StockSummary


def get_row_by_name(table, name, taildel):
    headers = table.row_values(0)
    index = headers.index(name)
    ctype = table.cell_type(1, index)
    # ctype： 0 empty, 1 string, 2 number, 3 date, 4 boolean, 5 error

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
    data = xlrd.open_workbook('C:\\Users\\zhouz\\OneDrive\\理财\\finance\\我的水平.xlsm')
    table = data.sheet_by_name('赌球')
    return get_row_by_name(table, '日期', True), get_row_by_name(table, '阶段性盈利', True)

def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]


def round_up(value):
    # 替换内置round函数,实现保留2位小数的精确四舍五入
    return round(value + 0.00001, 2)


def check_stock_data():
    data = xlrd.open_workbook('C:\\Users\\zhouz\\OneDrive\\理财\\finance\\我的水平.xlsm')
    table = data.sheet_by_name('场内交割单')
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
            assert code == get_key(code2name, name), "stock name and code conflict"
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
        elif buy_type == "分红":
            code2stock_summary[code].add(0, 0.0, table.cell(line, headers.index('发生金额')).value)
            assert code2stock_summary[code].position == -table.cell(line, headers.index('成交数量')).value, "分红数量有误"
        else:
            assert False, "stock buy_type error"

        # 00-深证A股，60-上证A股，300-创业板
        # 15、16、18-深证场内基金，50、51、52-上证场内基金
        # 12-深证转债，11-上证转债
        # 检查手续费
        volume = table.cell(line, headers.index('成交金额')).value
        commission = round_up(abs(volume) * 0.00016)
        stamp_tax = 0.0
        other = round_up(abs(volume) * 0.00002)
        if buy_type == "分红" or buy_type == "中签":
            commission = other = 0.0
        else:
            if code[:2] == "hk":
                # TODO
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
                commission = round_up(abs(volume) * 0.0001)
                other = 0
                if code[:2] == "11" and commission < 1.0:
                    commission = 1.0
            else:
                assert False, "stock code error"
        assert table.cell(line, headers.index('手续费')).value == commission, "股票手续费错误"
        assert table.cell(line, headers.index('印花税')).value == stamp_tax, "股票印花税错误"
        if table.cell(line, headers.index('委托号')).value != 25037:
            assert table.cell(line, headers.index('其他杂费')).value == other, "股票其它杂费错误"

        # 计算年化率
        tas.append((code, xlrd.xldate.xldate_as_datetime(table.cell(line, headers.index('时间')).value, 0),
                    table.cell(line, headers.index('发生金额')).value))
    return code2stock_summary, tas


def get_fund_data():
    data = xlrd.open_workbook('C:\\Users\\zhouz\\OneDrive\\理财\\finance\\我的水平.xlsm')
    table = data.sheet_by_name('场外基金')
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
        elif buy_type == "分红":
            code2stock_summary[code].add(table.cell(line, headers.index('份额')).value, 0.0,
                                         table.cell(line, headers.index('总额')).value)
        else:
            assert False, "stock buy_type error"

        # 计算年化率
        tas.append((code, xlrd.xldate.xldate_as_datetime(table.cell(line, headers.index('时间')).value, 0),
                    table.cell(line, headers.index('总计')).value))
    return code2stock_summary, tas


if __name__ == "__main__":
    #check_stock_data()
    get_fund_data()

