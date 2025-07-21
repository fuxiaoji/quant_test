import akshare as ak
import pandas as pd

def fetch_etf_data(pool_list, etf_names, start_date, end_date):
    print("正在获取ETF历史数据...")
    data_dict = {}
    for i, symbol in enumerate(pool_list):
        try:
            temp_df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if '日期' not in temp_df.columns or '收盘' not in temp_df.columns:
                print(f"{symbol} 数据字段不匹配，实际字段: {temp_df.columns}")
                continue
            temp_df = temp_df[['日期', '收盘']]
            temp_df.columns = ['date', symbol]
            temp_df['date'] = pd.to_datetime(temp_df['date'])
            temp_df.set_index('date', inplace=True)
            data_dict[symbol] = temp_df[symbol]
            print(f"已获取 {symbol}({etf_names[i]}) 数据")
        except Exception as e:
            print(f"获取 {symbol} 数据时出错: {e}")
    if data_dict:
        data = pd.DataFrame(data_dict).sort_index()
        print(f"数据合并完成，共{len(data)}条记录")
        print("数据概览:")
        print(data.head(10))
        return data
    else:
        print("未能获取任何数据")
        return None