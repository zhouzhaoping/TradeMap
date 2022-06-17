import akshare as ak
import pandas as pd
import time

# https://www.akshare.xyz/data/index.html
stock_zh_a_spot_df =pd.DataFrame()
stock_hk_spot_df = pd.DataFrame()
bond_zh_hs_cov_spot_df = pd.DataFrame()
stock_zh_index_spot_df = pd.DataFrame()
fund_etf_fund_spot_df = pd.DataFrame()
fund_open_fund_spot_df = pd.DataFrame()


def get_all():
    pass
    # try:
    #     print("get A stock information")
    #     stock_zh_a_spot_df = ak.stock_zh_a_spot()
    #     stock_zh_a_spot_df.to_csv('data\stock_zh_a.csv')
    # except:
    #     print("error")
    #
    # try:
    #     print("get HK stock information")
    #     stock_hk_spot_df = ak.stock_hk_spot()
    #     stock_hk_spot_df.to_csv('data\stock_hk.csv')
    # except:
    #     print("error")

    # try:
    #     print("get etf fund information")
    #     etf_df = ak.fund_etf_category_sina(symbol="ETF基金")
    #     lof_df = ak.fund_etf_category_sina(symbol="LOF基金")
    #     fund_etf_fund_spot_df = pd.concat([etf_df, lof_df])
    #     fund_etf_fund_spot_df.to_csv('data\etf_fund.csv')
    # except:
    #     print("error")

    # try:
    #     print("get open fund information")
    #     fund_open_fund_spot_df = ak.fund_em_value_estimation()
    #     fund_open_fund_spot_df.to_csv('data\open_fund.csv')
    #     print(fund_open_fund_spot_df.columns.tolist()[2])
    # except:
    #     print("error")

    # try:
    #     print("get bond information")
    #     bond_zh_hs_cov_spot_df = ak.bond_zh_hs_cov_spot()
    #     bond_zh_hs_cov_spot_df.to_csv('data\\bond_zh_hs.csv')
    # except:
    #     print("error")

    # try:
    #     print("get index information")
    #     stock_zh_index_spot_df = ak.stock_zh_index_spot()
    #     stock_zh_index_spot_df.to_csv('data\stock_zh_index.csv')
    # except:
    #     print("error")


def get_stock_price(stock_code):
    global stock_zh_a_spot_df
    global stock_hk_spot_df
    if stock_zh_a_spot_df.empty:
        print("get A stock information")
        stock_zh_a_spot_df = pd.read_csv('data\stock_zh_a.csv', dtype={'code': str, 'trade': float})
    if stock_hk_spot_df.empty:
        print("get HK stock information")
        stock_hk_spot_df = pd.read_csv('data\stock_hk.csv', dtype={'symbol': str, 'lasttrade': float})
    if stock_code[:2] == "hk":
        return stock_hk_spot_df.set_index('symbol').at[stock_code[2:], 'lasttrade']
    elif stock_code == '689009':
        return 64.0
    else:
        return stock_zh_a_spot_df.set_index('code').at[stock_code, 'trade']


def get_etf_fund_price(fund_code):
    global fund_etf_fund_spot_df
    if fund_etf_fund_spot_df.empty:
        print("get etf fund information")
        fund_etf_fund_spot_df = pd.read_csv('data\etf_fund.csv', dtype={'code': str, 'trade': float})
    return fund_etf_fund_spot_df.set_index('code').at[fund_code, 'trade']


# 场外基金没有合适的接口，所以用估算接口替代
def get_open_fund_price(fund_code):
    global fund_open_fund_spot_df
    if fund_open_fund_spot_df.empty:
        print("get open fund information")
        fund_open_fund_spot_df = pd.read_csv('data\open_fund.csv', dtype={'基金代码': str})
    return float(fund_open_fund_spot_df.set_index('基金代码').at[fund_code, fund_open_fund_spot_df.columns.tolist()[3]])


def get_bond_price(bond_code):
    global bond_zh_hs_cov_spot_df
    if bond_zh_hs_cov_spot_df.empty:
        print("get bond information")
        bond_zh_hs_cov_spot_df = pd.read_csv('data\\bond_zh_hs.csv', dtype={'code': str, 'trade': float})
    try:
        return bond_zh_hs_cov_spot_df.set_index('code').at[bond_code, 'trade']
    except:
        return 100.0

def get_index_price(index_code):
    global stock_zh_index_spot_df
    if stock_zh_index_spot_df.empty:
        print("get index information")
        stock_zh_index_spot_df = pd.read_csv('data\stock_zh_index.csv', dtype={'code': str, 'trade': float})
    return stock_zh_index_spot_df.set_index('code').at[index_code, 'trade']


if __name__ == "__main__":
    # A股（不含CDR、新三板）
    print("000001", get_stock_price("000001"))
    # 可转债
    print("127048", get_bond_price("127048"))
    # 港股
    print("hk00700", get_stock_price("hk00700"))
    # 指数
    print("000922", get_index_price("000922"))#这个过不去
    # 场内基金
    print("501029", get_etf_fund_price("501029")) #LOF
    print("512260", get_etf_fund_price("512260")) #ETF
    # 场外基金（估算）
    print("003318", get_open_fund_price("003318"))