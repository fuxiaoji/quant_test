# 通用基础包
import os
import numpy as np
import pandas as pd
from datetime import datetime

# 画图与分析
import matplotlib.pyplot as plt


# sklearn（如动量策略用到）
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# 项目内部模块
from strategies.macd_strategy import MACDStrategy
from strategies.momentum_strategy import MomentumStrategy
from quant_part.plot_nav import plot_nav
from quant_part.report_detail import report_detail
from data_manager import get_etf_data

if __name__ == "__main__":
    pool_list = ['510300','510880', '159915', '513100', '518880']
    etf_names = ['沪深300ETF', '红利ETF','创业板ETF','纳指ETF', '黄金ETF']
    start_date = '20200101'
    end_date = datetime.now().strftime('%Y%m%d')

    # 策略选择：macd 或 momentum
    strategy_type = 'macd'  # 可改为 'momentum'

    if strategy_type == 'macd':
        strategy = MACDStrategy(pool_list, etf_names, start_date, end_date, short=12, long=26, signal=9)
        strategy.fetch_data()
        strategy.run_strategy()
        strategy.show_results()
        plot_nav(strategy.data, strategy.name_list, etf_names)
    elif strategy_type == 'momentum':
        strategy = MomentumStrategy(pool_list, etf_names, start_date, end_date, N=20)
        strategy.fetch_data()
        strategy.calculate_momentum()
        strategy.show_latest_momentum()
        strategy.run_strategy()
        strategy.show_results()
        plot_nav(strategy.data, strategy.name_list, etf_names)
    else:
        print("未知策略类型") 