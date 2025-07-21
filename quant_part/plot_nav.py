import matplotlib.pyplot as plt

def plot_nav(data, name_list):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_xlabel('日期')
    ax.set_ylabel('净值')
    for name in name_list + ['轮动策略']:
        if name in name_list:
            data[name + '净值'] = data[name] / data[name].iloc[0]
            ax.plot(data[name + '净值'].index, data[name + '净值'].values, linestyle='--', label=name)
        else:
            ax.plot(data['轮动策略净值'].index, data['轮动策略净值'].values, linestyle='-', color='#FF8124', label='轮动策略')
    ax.legend(name_list + ['轮动策略'])
    ax.set_title('轮动策略净值曲线对比')
    plt.tight_layout()
    plt.show()