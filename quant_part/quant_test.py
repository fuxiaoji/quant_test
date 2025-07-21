import akshare as ak
import numpy as np
import pandas as pd
from datetime import datetime

# ETF代码列表
# 510300：沪深300ETF，代表大盘
# 510500：中证500ETF，代表小盘  
# 510880：红利ETF，代表价值
# 159915：创业板ETF，代表成长
pool_list = ['510300', '510500', '510880', '159915']
etf_names = ['沪深300ETF', '中证500ETF', '红利ETF', '创业板ETF']

# 设置起始日期
start_date = '20241001'
end_date = datetime.now().strftime('%Y%m%d')

# 获取ETF历史数据
print("正在获取ETF历史数据...")
data_dict = {}

for i, symbol in enumerate(pool_list):
    try:
        # 使用fund_etf_hist_em获取ETF历史数据
        temp_df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        
        # 重命名收盘价列
        temp_df = temp_df[['日期', '收盘']]
        temp_df.columns = ['date', symbol]
        temp_df['date'] = pd.to_datetime(temp_df['date'])
        temp_df.set_index('date', inplace=True)
        
        data_dict[symbol] = temp_df[symbol]
        print(f"已获取 {symbol}({etf_names[i]}) 数据")
        
    except Exception as e:
        print(f"获取 {symbol} 数据时出错: {e}")

# 合并数据
if data_dict:
    data = pd.DataFrame(data_dict)
    data = data.sort_index()
    print(f"数据合并完成，共{len(data)}条记录")
    print("数据概览:")
    print(data.head(10))
else:
    print("未能获取任何数据")
    exit()

# 动量长度
N = 20

# 计算每日涨跌幅和N日涨跌幅
name_list = data.columns.tolist()

for name in name_list:
    # 计算日收益率
    data['日收益率_'+name] = data[name] / data[name].shift(1) - 1.0
    # 计算N日涨跌幅（动量指标）
    data['涨幅_'+name] = data[name] / data[name].shift(N+1) - 1.0

# 去掉缺失值
data = data.dropna()

print(f"\n去除缺失值后，共{len(data)}条记录")
print(f"\n各ETF的{N}日动量数据（前10行）:")
momentum_cols = ['涨幅_'+v for v in name_list]
print(data[momentum_cols].head(10))

# 计算统计信息
print(f"\n各ETF的{N}日动量统计信息:")
print(data[momentum_cols].describe())

# 显示最新的动量数据
print(f"\n最新的{N}日动量数据:")
latest_momentum = data[momentum_cols].iloc[-1]
for i, col in enumerate(momentum_cols):
    etf_code = col.replace('涨幅_', '')
    etf_name = etf_names[pool_list.index(etf_code)]
    print(f"{etf_code}({etf_name}): {latest_momentum[col]:.4f} ({latest_momentum[col]*100:.2f}%)")

# 取出每日涨幅最大的证券
data['信号'] = data[['涨幅_'+v for v in name_list]].idxmax(axis=1).str.replace('涨幅_', '')
# 今日的涨幅由昨日的持仓产生
data['信号'] = data['信号'].shift(1)
data = data.dropna()
data['轮动策略日收益率'] = data.apply(lambda x: x['日收益率_'+x['信号']], axis=1) 
# 第一天尾盘交易，当日涨幅不纳入
data.loc[data.index[0],'轮动策略日收益率'] = 0.0
data['轮动策略净值'] = (1.0 + data['轮动策略日收益率']).cumprod()

# 打印最终结果表格
print(f"\n轮动策略结果表格（前10行）:")
result_table = data[['涨幅_'+v for v in name_list]+['信号','轮动策略日收益率','轮动策略净值']]
print(result_table.head(10))

print(f"\n轮动策略结果表格（最后10行）:")
print(result_table.tail(10))

# 打印策略绩效统计
print(f"\n策略绩效统计:")
total_return = data['轮动策略净值'].iloc[-1] - 1
annual_return = (data['轮动策略净值'].iloc[-1] ** (252/len(data))) - 1
volatility = data['轮动策略日收益率'].std() * np.sqrt(252)
sharpe_ratio = annual_return / volatility if volatility > 0 else 0
max_drawdown = (data['轮动策略净值'] / data['轮动策略净值'].cummax() - 1).min()

print(f"总收益率: {total_return:.4f} ({total_return*100:.2f}%)")
print(f"年化收益率: {annual_return:.4f} ({annual_return*100:.2f}%)")
print(f"年化波动率: {volatility:.4f} ({volatility*100:.2f}%)")
print(f"夏普比率: {sharpe_ratio:.4f}")
print(f"最大回撤: {max_drawdown:.4f} ({max_drawdown*100:.2f}%)")

# 各ETF持仓统计
print(f"\n各ETF持仓天数统计:")
signal_counts = data['信号'].value_counts()
for etf_code in pool_list:
    if etf_code in signal_counts.index:
        etf_name = etf_names[pool_list.index(etf_code)]
        days = signal_counts[etf_code]
        percentage = days / len(data) * 100
        print(f"{etf_code}({etf_name}): {days}天 ({percentage:.1f}%)")
    else:
        etf_name = etf_names[pool_list.index(etf_code)]
        print(f"{etf_code}({etf_name}): 0天 (0.0%)")


import matplotlib.pyplot as plt

# 显示中文设置
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

# 绘制净值曲线图
fig, ax = plt.subplots(figsize=(15, 6))
ax.set_xlabel('日期')
ax.set_ylabel('净值')
for name in name_list+['轮动策略']:
    if name in name_list:
        data[name+'净值'] = data[name]/data[name].iloc[0]
        ax.plot(data[name+'净值'].index, data[name+'净值'].values, linestyle='--')
    else:
        ax.plot(data[name+'净值'].index, data[name+'净值'].values, linestyle='-', color='#FF8124')

# 显示图例和标题
ax.legend(name_list+['轮动策略'])
ax.set_title('轮动策略净值曲线对比 ')

plt.show()