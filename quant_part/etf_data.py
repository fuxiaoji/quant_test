import akshare as ak
import pandas as pd

def fetch_etf_data(pool_list, etf_names, start_date, end_date):
    """
    拉取多个ETF的历史日线数据（前复权），返回DataFrame，索引为日期，列为ETF代码的收盘价。

    参数：
    - pool_list: ETF代码列表，如['510300', '510880']
    - etf_names: ETF名称列表，与pool_list对应
    - start_date: 起始日期，格式'YYYYMMDD'，如'20120101'
    - end_date: 结束日期，格式'YYYYMMDD'，如'20250723'

    返回：
    - pd.DataFrame，index为日期(datetime)，columns为ETF代码，值为复权后收盘价
    """
    print("正在获取ETF历史数据...")
    data_dict = {}

    for i, symbol in enumerate(pool_list):
        try:
            temp_df = ak.fund_etf_hist_em(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            # 检查字段
            if temp_df.empty:
                print(f"{symbol} 数据为空，跳过")
                continue
            if '日期' not in temp_df.columns or '收盘' not in temp_df.columns:
                print(f"{symbol} 数据字段不匹配，实际字段: {temp_df.columns.tolist()}")
                continue

            temp_df = temp_df[['日期', '收盘']].copy()
            temp_df['日期'] = pd.to_datetime(temp_df['日期'])
            temp_df.set_index('日期', inplace=True)
            temp_df.rename(columns={'收盘': symbol}, inplace=True)

            # 丢弃收盘价缺失数据
            temp_df = temp_df[temp_df[symbol].notnull()]
            if temp_df.empty:
                print(f"{symbol} 处理后无有效数据，跳过")
                continue

            data_dict[symbol] = temp_df[symbol]
            print(f"已获取 {symbol} ({etf_names[i]}) 数据，记录数：{len(temp_df)}")

        except Exception as e:
            print(f"获取 {symbol} 数据时出错: {e}")

    if data_dict:
        data = pd.DataFrame(data_dict)
        data.sort_index(inplace=True)
        print(f"数据合并完成，共 {len(data)} 条记录")
        print("数据预览（前10行）：")
        print(data.head(10))
        return data
    else:
        print("未能获取任何数据")
        return None
