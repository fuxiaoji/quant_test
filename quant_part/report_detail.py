import numpy as np

def report_detail(data, pool_list, etf_names):
    print(f"\n轮动策略结果表格（前10行）:")
    momentum_cols = ['涨幅_'+v for v in pool_list]
    result_table = data[momentum_cols+['信号','轮动策略日收益率','轮动策略净值']]
    print(result_table.head(10))
    print(f"\n轮动策略结果表格（最后10行）:")
    print(result_table.tail(10))

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

    print(f"\n各ETF持仓天数统计:")
    signal_counts = data['信号'].value_counts()
    for etf_code in pool_list:
        etf_name = etf_names[pool_list.index(etf_code)]
        days = signal_counts.get(etf_code, 0)
        percentage = days / len(data) * 100
        print(f"{etf_code}({etf_name}): {days}天 ({percentage:.1f}%)")

    # === 详细回测分析报告（替代quantstats）===
    print("\n=== 详细回测分析报告 ===")
    strategy_returns = data['轮动策略日收益率'].copy()

    # 基准对比分析（510300）
    if '510300' in data.columns:
        benchmark_returns = data['日收益率_510300'].copy()
        benchmark_nav = (1 + benchmark_returns).cumprod()

        print(f"\n基准对比分析（沪深300ETF）:")
        benchmark_total_return = benchmark_nav.iloc[-1] - 1
        benchmark_annual_return = (benchmark_nav.iloc[-1] ** (252/len(benchmark_nav))) - 1
        benchmark_volatility = benchmark_returns.std() * np.sqrt(252)
        benchmark_sharpe = benchmark_annual_return / benchmark_volatility if benchmark_volatility > 0 else 0
        benchmark_max_dd = (benchmark_nav / benchmark_nav.cummax() - 1).min()

        print(f"基准总收益率: {benchmark_total_return:.4f} ({benchmark_total_return*100:.2f}%)")
        print(f"基准年化收益率: {benchmark_annual_return:.4f} ({benchmark_annual_return*100:.2f}%)")
        print(f"基准年化波动率: {benchmark_volatility:.4f} ({benchmark_volatility*100:.2f}%)")
        print(f"基准夏普比率: {benchmark_sharpe:.4f}")
        print(f"基准最大回撤: {benchmark_max_dd:.4f} ({benchmark_max_dd*100:.2f}%)")

        # 超额收益分析
        excess_return = total_return - benchmark_total_return
        excess_annual_return = annual_return - benchmark_annual_return
        tracking_error = (strategy_returns - benchmark_returns).std() * np.sqrt(252)
        information_ratio = excess_annual_return / tracking_error if tracking_error > 0 else 0

        print(f"\n超额收益分析:")
        print(f"超额总收益: {excess_return:.4f} ({excess_return*100:.2f}%)")
        print(f"超额年化收益: {excess_annual_return:.4f} ({excess_annual_return*100:.2f}%)")
        print(f"跟踪误差: {tracking_error:.4f} ({tracking_error*100:.2f}%)")
        print(f"信息比率: {information_ratio:.4f}")

    # 风险指标分析
    print(f"\n风险指标分析:")
    winning_rate = (strategy_returns > 0).sum() / len(strategy_returns)
    loss_rate = (strategy_returns < 0).sum() / len(strategy_returns)
    avg_win = strategy_returns[strategy_returns > 0].mean() if (strategy_returns > 0).any() else 0
    avg_loss = strategy_returns[strategy_returns < 0].mean() if (strategy_returns < 0).any() else 0
    win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')

    print(f"胜率: {winning_rate:.4f} ({winning_rate*100:.2f}%)")
    print(f"败率: {loss_rate:.4f} ({loss_rate*100:.2f}%)")
    print(f"平均盈利: {avg_win:.4f} ({avg_win*100:.2f}%)")
    print(f"平均亏损: {avg_loss:.4f} ({avg_loss*100:.2f}%)")
    print(f"盈亏比: {win_loss_ratio:.4f}")

    # VaR风险度量
    var_95 = np.percentile(strategy_returns, 5)
    var_99 = np.percentile(strategy_returns, 1)
    cvar_95 = strategy_returns[strategy_returns <= var_95].mean()

    print(f"\n风险度量:")
    print(f"95% VaR: {var_95:.4f} ({var_95*100:.2f}%)")
    print(f"99% VaR: {var_99:.4f} ({var_99*100:.2f}%)")
    print(f"95% CVaR: {cvar_95:.4f} ({cvar_95*100:.2f}%)")

    # 月度/年度收益分析
    print(f"\n时间维度收益分析:")
    monthly_returns = strategy_returns.resample('M').apply(lambda x: (1+x).prod()-1)
    yearly_returns = strategy_returns.resample('Y').apply(lambda x: (1+x).prod()-1)

    print(f"月度收益统计:")
    print(f"  平均月收益: {monthly_returns.mean():.4f} ({monthly_returns.mean()*100:.2f}%)")
    print(f"  月收益标准差: {monthly_returns.std():.4f} ({monthly_returns.std()*100:.2f}%)")
    print(f"  正收益月份: {(monthly_returns > 0).sum()}/{len(monthly_returns)} ({(monthly_returns > 0).sum()/len(monthly_returns)*100:.1f}%)")

    if len(yearly_returns) > 1:
        print(f"年度收益统计:")
        for year, ret in yearly_returns.items():
            print(f"  {year.year}年: 收益率 {ret:.4f} ({ret*100:.2f}%)")