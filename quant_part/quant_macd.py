import akshare as ak
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import quantstats as qs
from plot_nav import plot_nav  # 保证已导入
from report_detail import report_detail
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from plot_nav import plot_nav
from etf_data import fetch_etf_data


class ETFMACDStrategy:
    def __init__(self, pool_list, etf_names, start_date, end_date, short=12, long=26, signal=9):
        self.pool_list = pool_list
        self.etf_names = etf_names
        self.start_date = start_date
        self.end_date = end_date
        self.short = short  # 短期EMA参数
        self.long = long    # 长期EMA参数
        self.signal = signal # 信号线参数
        self.data = None
        self.name_list = pool_list
        self.positions = {code: 0 for code in pool_list}  # 每个ETF的持仓状态(0/1)
        self.weight_per_etf = 1.0 / len(pool_list)  # 每个ETF分配的资金权重

    def fetch_data(self):
        """获取ETF数据"""
        self.data = fetch_etf_data(self.pool_list, self.etf_names, self.start_date, self.end_date)
        if self.data is None:
            print("数据获取失败")
            exit()

    def calculate_macd(self, price_series, short=12, long=26, signal=9):
        """计算MACD指标"""
        if len(price_series) < long:
            return pd.DataFrame(columns=['diff', 'dea', 'macd'])
            
        ema_short = price_series.ewm(span=short, adjust=False).mean()
        ema_long = price_series.ewm(span=long, adjust=False).mean()
        diff = ema_short - ema_long  # DIFF线
        dea = diff.ewm(span=signal, adjust=False).mean()  # DEA线(信号线)
        macd = 2 * (diff - dea)  # MACD柱状图
        
        return pd.DataFrame({
            'diff': diff,
            'dea': dea,
            'macd': macd
        })

    def generate_macd_signals(self):
        """为所有ETF生成MACD交易信号"""
        print(f"正在计算MACD信号... (参数: {self.short}, {self.long}, {self.signal})")
        
        # 确保有足够的数据计算MACD
        min_required_days = max(self.long * 2, 60)  # 至少需要长期EMA的2倍数据
        if len(self.data) < min_required_days:
            print(f"警告: 数据不足，需要至少{min_required_days}天数据，当前只有{len(self.data)}天")
            print("建议调整开始日期或MACD参数")
        
        for code in self.name_list:
            price_series = self.data[code].dropna()
            
            # 计算MACD
            macd_df = self.calculate_macd(price_series, self.short, self.long, self.signal)
            
            if macd_df.empty or len(macd_df) < 2:
                print(f"警告: {code} 数据不足，无法计算MACD")
                # 创建全零信号序列
                self.data[f'信号_{code}'] = 0
                self.data[f'diff_{code}'] = np.nan
                self.data[f'dea_{code}'] = np.nan
                self.data[f'macd_{code}'] = np.nan
                continue
            
            # 生成交易信号
            signals = pd.Series(0, index=price_series.index)
            
            if len(macd_df) >= 2:
                # 金叉：DIFF上穿DEA (买入信号)
                golden_cross = ((macd_df['diff'] > macd_df['dea']) & 
                               (macd_df['diff'].shift(1) <= macd_df['dea'].shift(1)))
                
                # 死叉：DIFF下穿DEA (卖出信号)  
                death_cross = ((macd_df['diff'] < macd_df['dea']) & 
                              (macd_df['diff'].shift(1) >= macd_df['dea'].shift(1)))
                
                signals.loc[golden_cross] = 1   # 买入信号
                signals.loc[death_cross] = -1   # 卖出信号
            
            # 将信号添加到主数据框，确保索引对齐
            self.data[f'信号_{code}'] = signals.reindex(self.data.index, fill_value=0)
            self.data[f'diff_{code}'] = macd_df['diff'].reindex(self.data.index)
            self.data[f'dea_{code}'] = macd_df['dea'].reindex(self.data.index)
            self.data[f'macd_{code}'] = macd_df['macd'].reindex(self.data.index)
            
            # 统计信号数量
            buy_signals = (signals == 1).sum()
            sell_signals = (signals == -1).sum()
            print(f"{code}: 买入信号{buy_signals}次, 卖出信号{sell_signals}次")

    def calculate_returns(self):
 
        for code in self.name_list:
            # 计算日收益率
            self.data[f'日收益率_{code}'] = self.data[code].pct_change().fillna(0)
            
            # 计算涨幅（为了兼容report_detail.py）
            self.data[f'涨幅_{code}'] = self.data[code].pct_change().fillna(0)


    def run_strategy(self):
        """运行MACD策略回测"""
        print("开始运行MACD策略...")
        
        # 生成MACD信号
        self.generate_macd_signals()
        
        # 计算收益率
        self.calculate_returns()
        
        # 删除空值行
        signal_cols = [f'信号_{code}' for code in self.name_list]
        self.data = self.data.dropna(subset=signal_cols)
        
        if self.data.empty:
            print("错误: 处理后数据为空")
            return
        
        # 初始化持仓状态和策略收益
        portfolio_returns = []
        active_signals = []  # 记录当前持有的ETF
        
        print(f"回测数据范围: {self.data.index[0]} 到 {self.data.index[-1]}")
        print(f"每个ETF分配权重: {self.weight_per_etf:.4f}")
        
        for date in self.data.index:
            daily_return = 0.0
            current_holdings = []
            
            for code in self.name_list:
                signal = self.data.loc[date, f'信号_{code}']
                price_return = self.data.loc[date, f'日收益率_{code}']
                
                # 处理信号
                if signal == 1:  # 金叉买入
                    if self.positions[code] == 0:
                        self.positions[code] = 1
                        print(f"{date.date()} {code} MACD金叉买入")
                elif signal == -1:  # 死叉卖出
                    if self.positions[code] == 1:
                        self.positions[code] = 0
                        print(f"{date.date()} {code} MACD死叉卖出")
                
                # 如果持仓，计算收益
                if self.positions[code] == 1:
                    daily_return += self.weight_per_etf * price_return
                    current_holdings.append(code)
            
            portfolio_returns.append(daily_return)
            active_signals.append(','.join(current_holdings) if current_holdings else 'Cash')
        
        # 将结果添加到数据框
        self.data['轮动策略日收益率'] = portfolio_returns
        self.data['信号'] = active_signals
        
        # 计算累计净值
        self.data['轮动策略净值'] = (1.0 + self.data['轮动策略日收益率']).cumprod()
        
        print(f"策略回测完成！")
        print(f"最终净值: {self.data['轮动策略净值'].iloc[-1]:.4f}")
        print(f"总收益率: {(self.data['轮动策略净值'].iloc[-1] - 1.0) * 100:.2f}%")

    def show_latest_signals(self):
        """显示最新的MACD信号状态"""
        # 检查是否已经生成信号
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
            
            # 检查MACD列是否存在
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
        """显示策略结果"""
        print("\n策略统计信息:")
        total_days = len(self.data)
        holding_days = len(self.data[self.data['信号'] != 'Cash'])
        holding_ratio = holding_days / total_days * 100
        
        print(f"总交易日数: {total_days}")
        print(f"持仓日数: {holding_days}")
        print(f"持仓比例: {holding_ratio:.2f}%")
        
        # 显示最新信号
        self.show_latest_signals()
        
        # 调用详细报告
        report_detail(self.data, self.pool_list, self.etf_names)

    def calculate_momentum(self):
        """为兼容性保留的空方法"""
        pass

    def show_latest_momentum(self):
        """为兼容性保留的空方法，改为显示基本信息"""
        print(f"\n策略信息:")
        print(f"ETF池: {self.pool_list}")
        print(f"MACD参数: 短期EMA={self.short}, 长期EMA={self.long}, 信号线={self.signal}")
        print(f"每ETF权重: {self.weight_per_etf:.4f}")
        print("注意: MACD信号将在运行策略后显示")


if __name__ == "__main__":
    pool_list = ['510300','510880', '159915', '513100', '518880']
    etf_names = ['沪深300ETF', '红利ETF','创业板ETF','纳指ETF', '黄金ETF']
    start_date = '20250101'
    end_date = datetime.now().strftime('%Y%m%d')
    
    # 创建MACD策略实例
    strategy = ETFMACDStrategy(pool_list, etf_names, start_date, end_date, short=12, long=26, signal=9)
    
    # 运行策略
    strategy.fetch_data()
    strategy.calculate_momentum()  # 兼容性调用
    strategy.show_latest_momentum()  # 显示策略基本信息
    strategy.run_strategy()  # 运行策略，生成MACD信号
    strategy.show_results()  # 显示结果，包括最新MACD信号
    plot_nav(strategy.data, strategy.name_list, etf_names) # 传入etf_names，图例显示