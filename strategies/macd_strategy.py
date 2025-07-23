import numpy as np
import pandas as pd
from datetime import datetime
from data_manager import get_etf_data
from quant_part.plot_nav import plot_nav
from quant_part.report_detail import report_detail

class MACDStrategy:
    def __init__(self, pool_list, etf_names, start_date, end_date, short=12, long=26, signal=9):
        self.pool_list = pool_list
        self.etf_names = etf_names
        self.start_date = start_date
        self.end_date = end_date
        self.short = short
        self.long = long
        self.signal = signal
        self.data = None
        self.name_list = pool_list
        self.positions = {code: 0 for code in pool_list}
        self.weight_per_etf = 1.0 / len(pool_list)

    def fetch_data(self):
        self.data = get_etf_data(self.pool_list, self.etf_names, self.start_date, self.end_date)
        if self.data is None:
            print("数据获取失败")
            exit()

    def calculate_macd(self, price_series, short=12, long=26, signal=9):
        if len(price_series) < long:
            return pd.DataFrame(columns=['diff', 'dea', 'macd'])
        ema_short = price_series.ewm(span=short, adjust=False).mean()
        ema_long = price_series.ewm(span=long, adjust=False).mean()
        diff = ema_short - ema_long
        dea = diff.ewm(span=signal, adjust=False).mean()
        macd = 2 * (diff - dea)
        return pd.DataFrame({'diff': diff, 'dea': dea, 'macd': macd})

    def generate_macd_signals(self):
        print(f"正在计算MACD信号... (参数: {self.short}, {self.long}, {self.signal})")
        min_required_days = max(self.long * 2, 60)
        if len(self.data) < min_required_days:
            print(f"警告: 数据不足，需要至少{min_required_days}天数据，当前只有{len(self.data)}天")
            print("建议调整开始日期或MACD参数")
        for code in self.name_list:
            price_series = self.data[code].dropna()
            macd_df = self.calculate_macd(price_series, self.short, self.long, self.signal)
            if macd_df.empty or len(macd_df) < 2:
                print(f"警告: {code} 数据不足，无法计算MACD")
                self.data[f'信号_{code}'] = 0
                self.data[f'diff_{code}'] = np.nan
                self.data[f'dea_{code}'] = np.nan
                self.data[f'macd_{code}'] = np.nan
                continue
            signals = pd.Series(0, index=price_series.index)
            if len(macd_df) >= 2:
                golden_cross = ((macd_df['diff'] > macd_df['dea']) & (macd_df['diff'].shift(1) <= macd_df['dea'].shift(1)))
                death_cross = ((macd_df['diff'] < macd_df['dea']) & (macd_df['diff'].shift(1) >= macd_df['dea'].shift(1)))
                signals.loc[golden_cross] = 1
                signals.loc[death_cross] = -1
            self.data[f'信号_{code}'] = signals.reindex(self.data.index, fill_value=0)
            self.data[f'diff_{code}'] = macd_df['diff'].reindex(self.data.index)
            self.data[f'dea_{code}'] = macd_df['dea'].reindex(self.data.index)
            self.data[f'macd_{code}'] = macd_df['macd'].reindex(self.data.index)
            buy_signals = (signals == 1).sum()
            sell_signals = (signals == -1).sum()
            print(f"{code}: 买入信号{buy_signals}次, 卖出信号{sell_signals}次")

    def calculate_returns(self):
        for code in self.name_list:
            self.data[f'日收益率_{code}'] = self.data[code].pct_change().fillna(0)
            self.data[f'涨幅_{code}'] = self.data[code].pct_change().fillna(0)

    def run_strategy(self):
        print("开始运行MACD策略...")
        self.generate_macd_signals()
        self.calculate_returns()
        signal_cols = [f'信号_{code}' for code in self.name_list]
        self.data = self.data.dropna(subset=signal_cols)
        if self.data.empty:
            print("错误: 处理后数据为空")
            return
        portfolio_returns = []
        active_signals = []
        print(f"回测数据范围: {self.data.index[0]} 到 {self.data.index[-1]}")
        print(f"每个ETF分配权重: {self.weight_per_etf:.4f}")
        for date in self.data.index:
            daily_return = 0.0
            current_holdings = []
            for code in self.name_list:
                signal = self.data.loc[date, f'信号_{code}']
                price_return = self.data.loc[date, f'日收益率_{code}']
                if signal == 1:
                    if self.positions[code] == 0:
                        self.positions[code] = 1
                        print(f"{date.date()} {code} MACD金叉买入")
                elif signal == -1:
                    if self.positions[code] == 1:
                        self.positions[code] = 0
                        print(f"{date.date()} {code} MACD死叉卖出")
                if self.positions[code] == 1:
                    daily_return += self.weight_per_etf * price_return
                    current_holdings.append(code)
            portfolio_returns.append(daily_return)
            active_signals.append(','.join(current_holdings) if current_holdings else 'Cash')
        self.data['轮动策略日收益率'] = portfolio_returns
        self.data['信号'] = active_signals
        self.data['轮动策略净值'] = (1.0 + self.data['轮动策略日收益率']).cumprod()
        print(f"策略回测完成！")
        print(f"最终净值: {self.data['轮动策略净值'].iloc[-1]:.4f}")
        print(f"总收益率: {(self.data['轮动策略净值'].iloc[-1] - 1.0) * 100:.2f}%")

    def show_latest_signals(self):
        signal_cols = [f'信号_{code}' for code in self.name_list]
        if not all(col in self.data.columns for col in signal_cols):
            print("MACD信号尚未生成，请先运行策略")
            return
        print(f"\n最新MACD信号状态:")
        latest_date = self.data.index[-1]
        for i, code in enumerate(self.name_list):
            try:
                etf_name = self.etf_names[i]
            except:
                etf_name = "未知ETF"
            signal = self.data.loc[latest_date, f'信号_{code}']
            position = self.positions[code]
            if f'diff_{code}' in self.data.columns:
                diff = self.data.loc[latest_date, f'diff_{code}']
                dea = self.data.loc[latest_date, f'dea_{code}']
                diff_text = f"DIFF:{diff:.4f} DEA:{dea:.4f}"
            else:
                diff_text = "MACD数据未计算"
            signal_text = "金叉买入" if signal == 1 else "死叉卖出" if signal == -1 else "无信号"
            position_text = "持仓" if position == 1 else "空仓"
            print(f"{code}({etf_name}): {signal_text} | {position_text} | {diff_text}")

    def show_results(self):
        print("\n策略统计信息:")
        total_days = len(self.data)
        holding_days = len(self.data[self.data['信号'] != 'Cash'])
        holding_ratio = holding_days / total_days * 100
        print(f"总交易日数: {total_days}")
        print(f"持仓日数: {holding_days}")
        print(f"持仓比例: {holding_ratio:.2f}%")
        self.show_latest_signals()
        report_detail(self.data, self.pool_list, self.etf_names)

    def calculate_momentum(self):
        pass

    def show_latest_momentum(self):
        print(f"\n策略信息:")
        print(f"ETF池: {self.pool_list}")
        print(f"MACD参数: 短期EMA={self.short}, 长期EMA={self.long}, 信号线={self.signal}")
        print(f"每ETF权重: {self.weight_per_etf:.4f}")
        print("注意: MACD信号将在运行策略后显示") 