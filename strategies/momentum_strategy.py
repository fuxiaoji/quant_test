import numpy as np
import pandas as pd
from datetime import datetime
from data_manager import get_etf_data
from quant_part.plot_nav import plot_nav
from quant_part.report_detail import report_detail
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class MomentumStrategy:
    def __init__(self, pool_list, etf_names, start_date, end_date, N=20):
        self.pool_list = pool_list
        self.etf_names = etf_names
        self.start_date = start_date
        self.end_date = end_date
        self.N = N
        self.data = None
        self.name_list = pool_list

    def fetch_data(self):
        self.data = get_etf_data(self.pool_list, self.etf_names, self.start_date, self.end_date)
        if self.data is None:
            exit()

    def calculate_score(self, srs, N=25):
        if srs.shape[0] < N:
            return np.nan
        x = np.arange(1, N+1)
        if srs.values[0] == 0:
            return np.nan
        y = srs.values / srs.values[0]
        if len(x) != len(y):
            return np.nan
        lr = LinearRegression().fit(x.reshape(-1, 1), y)
        slope = lr.coef_[0]
        r_squared = r2_score(y, lr.predict(x.reshape(-1, 1)))
        score = 10000 * slope * r_squared
        return score

    def show_latest_momentum(self):
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        latest_momentum = self.data[momentum_cols].iloc[-1]
        print(f"\n最新的{self.N}日动量数据:")
        for i, col in enumerate(momentum_cols):
            etf_code = col.replace('涨幅_', '')
            N = self.N
            try:
                etf_name = self.etf_names[self.pool_list.index(etf_code)]
            except ValueError:
                etf_name = "未知ETF"
            print(f"{etf_code}({etf_name}): {latest_momentum[col]:.4f} ({latest_momentum[col]*100:.2f}%)")

    def calculate_momentum(self):
        N = self.N if hasattr(self, 'N') else 25
        for name in self.name_list:
            self.data['日收益率_'+name] = self.data[name] / self.data[name].shift(1) - 1.0
            self.data['涨幅_'+name] = self.data[name] / self.data[name].shift(N) - 1.0
            self.data['得分_'+name] = self.data[name].rolling(N).apply(lambda x: self.calculate_score(x, N))
        relevant_cols = ['得分_'+v for v in self.name_list] + ['涨幅_'+v for v in self.name_list]
        self.data = self.data.dropna(subset=relevant_cols)
        print(f"\n各ETF的{N}日斜率得分（前10行）:")
        print(self.data[['得分_'+v for v in self.name_list]].head(10))
        print(f"\n各ETF的{N}日动量涨幅（前10行）:")
        print(self.data[['涨幅_'+v for v in self.name_list]].head(10))
        print(f"\n各ETF的{N}日动量统计信息:")
        print(self.data[['涨幅_'+v for v in self.name_list]].describe())

    def run_strategy(self):
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        self.data['信号'] = self.data[momentum_cols].idxmax(axis=1).str.replace('涨幅_', '')
        self.data['信号'] = self.data['信号'].shift(1)
        self.data = self.data.dropna()
        self.data['轮动策略日收益率'] = self.data.apply(lambda x: x['日收益率_'+x['信号']], axis=1)
        self.data.loc[self.data.index[0],'轮动策略日收益率'] = 0.0
        self.data['轮动策略净值'] = (1.0 + self.data['轮动策略日收益率']).cumprod()

    def show_results(self):
        report_detail(self.data, self.pool_list, self.etf_names) 