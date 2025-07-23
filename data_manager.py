import os
import pandas as pd
from quant_part.etf_data import fetch_etf_data
from datetime import datetime

def get_etf_data(pool_list, etf_names, start_date, end_date, data_path="etf_data_20120101_today.csv"):
    if not os.path.exists(data_path):
        print("本地无数据，正在下载2012年至今的全部数据...")
        all_data = fetch_etf_data(pool_list, etf_names, "20120101", datetime.now().strftime('%Y%m%d'))
        all_data.to_csv(data_path)
    else:
        all_data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    # 按回测日期切片
    return all_data.loc[start_date:end_date] 