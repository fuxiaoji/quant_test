import akshare as ak
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import quantstats as qstat

class ETFMomentumStrategy:
    def __init__(self, pool_list, etf_names, start_date, end_date, N=20):
        self.pool_list = pool_list
        self.etf_names = etf_names
        self.start_date = start_date
        self.end_date = end_date
        self.N = N
        self.data = None
        self.name_list = pool_list

    def fetch_data(self):
        print("正在获取ETF历史数据...")
        data_dict = {}
        for i, symbol in enumerate(self.pool_list):
            try:
                temp_df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=self.start_date, end_date=self.end_date, adjust="qfq")
                if '日期' not in temp_df.columns or '收盘' not in temp_df.columns:
                    print(f"{symbol} 数据字段不匹配，实际字段: {temp_df.columns}")
                    continue
                temp_df = temp_df[['日期', '收盘']]
                temp_df.columns = ['date', symbol]
                temp_df['date'] = pd.to_datetime(temp_df['date'])
                temp_df.set_index('date', inplace=True)
                data_dict[symbol] = temp_df[symbol]
                print(f"已获取 {symbol}({self.etf_names[i]}) 数据")
            except Exception as e:
                print(f"获取 {symbol} 数据时出错: {e}")
        if data_dict:
            self.data = pd.DataFrame(data_dict).sort_index()
            print(f"数据合并完成，共{len(self.data)}条记录")
            print("数据概览:")
            print(self.data.head(10))
        else:
            print("未能获取任何数据")
            exit()

    def calculate_momentum(self):
        for name in self.name_list:
            self.data['日收益率_'+name] = self.data[name] / self.data[name].shift(1) - 1.0
            self.data['涨幅_'+name] = self.data[name] / self.data[name].shift(self.N+1) - 1.0
        self.data = self.data.dropna()
        print(f"\n去除缺失值后，共{len(self.data)}条记录")
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        print(f"\n各ETF的{self.N}日动量数据（前10行）:")
        print(self.data[momentum_cols].head(10))
        print(f"\n各ETF的{self.N}日动量统计信息:")
        print(self.data[momentum_cols].describe())

    def show_latest_momentum(self):
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        latest_momentum = self.data[momentum_cols].iloc[-1]
        print(f"\n最新的{self.N}日动量数据:")
        for i, col in enumerate(momentum_cols):
            etf_code = col.replace('涨幅_', '')
            etf_name = self.etf_names[self.pool_list.index(etf_code)]
            print(f"{etf_code}({etf_name}): {latest_momentum[col]:.4f} ({latest_momentum[col]*100:.2f}%)")

    def run_strategy(self):
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        self.data['信号'] = self.data[momentum_cols].idxmax(axis=1).str.replace('涨幅_', '')
        self.data['信号'] = self.data['信号'].shift(1)
        self.data = self.data.dropna()
        self.data['轮动策略日收益率'] = self.data.apply(lambda x: x['日收益率_'+x['信号']], axis=1)
        self.data.loc[self.data.index[0],'轮动策略日收益率'] = 0.0
        self.data['轮动策略净值'] = (1.0 + self.data['轮动策略日收益率']).cumprod()

    def show_results(self):
        momentum_cols = ['涨幅_'+v for v in self.name_list]
        result_table = self.data[momentum_cols+['信号','轮动策略日收益率','轮动策略净值']]
        print(f"\n轮动策略结果表格（前10行）:")
        print(result_table.head(10))
        print(f"\n轮动策略结果表格（最后10行）:")
        print(result_table.tail(10))

        print(f"\n策略绩效统计:")
        total_return = self.data['轮动策略净值'].iloc[-1] - 1
        annual_return = (self.data['轮动策略净值'].iloc[-1] ** (252/len(self.data))) - 1
        volatility = self.data['轮动策略日收益率'].std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        max_drawdown = (self.data['轮动策略净值'] / self.data['轮动策略净值'].cummax() - 1).min()
        print(f"总收益率: {total_return:.4f} ({total_return*100:.2f}%)")
        print(f"年化收益率: {annual_return:.4f} ({annual_return*100:.2f}%)")
        print(f"年化波动率: {volatility:.4f} ({volatility*100:.2f}%)")
        print(f"夏普比率: {sharpe_ratio:.4f}")
        print(f"最大回撤: {max_drawdown:.4f} ({max_drawdown*100:.2f}%)")

        print(f"\n各ETF持仓天数统计:")
        signal_counts = self.data['信号'].value_counts()
        for etf_code in self.pool_list:
            etf_name = self.etf_names[self.pool_list.index(etf_code)]
            days = signal_counts.get(etf_code, 0)
            percentage = days / len(self.data) * 100
            print(f"{etf_code}({etf_name}): {days}天 ({percentage:.1f}%)")

        # === 集成 quantstats 回测报告 ===
        print("\n正在生成 quantstats 回测报告...")
        # 轮动策略净值和沪深300ETF净值都需存在
        if '轮动策略净值' in self.data.columns and '510300净值' in self.data.columns:
            qstat.reports.html(self.data['轮动策略净值'], benchmark=self.data['510300净值'],
                              title='轮动策略回测报告 ',
                              download_filename='轮动策略回测报告 .html')
            qstat.reports.basic(self.data['轮动策略净值'], benchmark=self.data['510300净值'])
        else:
            print("净值数据缺失，无法生成 quantstats 报告。")

    def plot(self):
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus']=False
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.set_xlabel('日期')
        ax.set_ylabel('净值')
        for name in self.name_list+['轮动策略']:
            if name in self.name_list:
                self.data[name+'净值'] = self.data[name]/self.data[name].iloc[0]
                ax.plot(self.data[name+'净值'].index, self.data[name+'净值'].values, linestyle='--')
            else:
                ax.plot(self.data['轮动策略净值'].index, self.data['轮动策略净值'].values, linestyle='-', color='#FF8124')
        ax.legend(self.name_list+['轮动策略'])
        ax.set_title('轮动策略净值曲线对比 ')
        plt.show()

if __name__ == "__main__":
    pool_list = ['510300', '510500', '510880', '159915']
    etf_names = ['沪深300ETF', '中证500ETF', '红利ETF', '创业板ETF']
    start_date = '20220101'
    end_date = datetime.now().strftime('%Y%m%d')
    strategy = ETFMomentumStrategy(pool_list, etf_names, start_date, end_date, N=20)
    strategy.fetch_data()
    strategy.calculate_momentum()
    strategy.show_latest_momentum()
    strategy.run_strategy()
    strategy.show_results()
    strategy.plot()