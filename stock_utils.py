import baostock as bs
import pandas as pd
from datetime import datetime,timedelta

def get_hs300_stocks():
    """
    获取上证300的股票代码
    :return:
    """
    # 登陆系统
    lg = bs.login()
    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    # 打印结果集
    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    # 登出系统
    bs.logout()
    return pd.DataFrame(hs300_stocks, columns=rs.fields)


def get_k_data_plus(code,start,end):
    """
    获取股票数据
    :param code: 股票代码
    :param start: 开始日期
    :param end: 结束日期
    :return: 返回dataframe格式的股票信息
    """
    # 登陆系统
    lg = bs.login()
    # 获取沪深A股历史K线数据
    rs = bs.query_history_k_data_plus(code,"date,code,open,high,low,close,preclose,volume,amount",
                                      start_date=start, end_date=end,
                                      frequency="d", adjustflag="3")
    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    # 登出系统
    bs.logout()
    return pd.DataFrame(data_list, columns=rs.fields)

def get_data_before_k_days(code,before_days):
    """
    获取今天以前k天到昨天的数据
    :param code: 股票代码
    :param before_days: k天以前
    :return: 返回dataframe格式的股票信息
    """
    cur_date = datetime.now()
    yesterday = (cur_date - timedelta(days=1)).strftime("%Y-%m-%d")
    start_day = (cur_date - timedelta(days=before_days)).strftime("%Y-%m-%d")
    return get_k_data_plus(code,start=start_day,end=yesterday)

def get_cash_flow(code):
    lg = bs.login()
    curr_year = int(datetime.now().strftime("%Y"))
    df_list = []
    for year in range(curr_year-5,curr_year+1):
        for quarter in [1,2,3,4]:
            # 季频现金流量
            cash_flow_list = []
            rs_cash_flow = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
            try:
                while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
                    cash_flow_list.append(rs_cash_flow.get_row_data())
            except:
                continue
            result = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)
            df_list.append(result)
    bs.logout()
    df_all = pd.concat(df_list)
    no_data_columns = ["CAToAsset","NCAToAsset","tangibleAssetToAsset","ebitToInterest"]
    df_all = df_all[[x for x in df_all.columns if x not in no_data_columns]]
    return df_all




if __name__ == '__main__':
    # stocks = get_hs300_stocks()
    # print(stocks)
    #
    # stock_data = get_k_data_plus("sh.600000",start="2023-03-20",end="2023-04-10")
    # print(stock_data)

    # history_data = get_data_before_k_days("sh.600000",30)
    # print(history_data)

    print(get_cash_flow("sh.600031"))