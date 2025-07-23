import matplotlib.pyplot as plt

def plot_nav(data, name_list, etf_names):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_xlabel('日期')
    ax.set_ylabel('净值')

    # 建立 ETF 代码 和 中文名称 的映射字典
    name_map = dict(zip(name_list, etf_names))

    for name in name_list + ['轮动策略']:
        if name in name_list:
            data[name + '净值'] = data[name] / data[name].iloc[0]
            label = name_map.get(name, name)  # 显示中文名
            ax.plot(data[name + '净值'].index, data[name + '净值'].values, linestyle='--', label=label)
        else:
            ax.plot(data['轮动策略净值'].index, data['轮动策略净值'].values, linestyle='-', color='#FF8124', label='轮动策略')

    ax.legend()
    ax.set_title('轮动策略净值曲线对比')
    plt.tight_layout()
    plt.show()
