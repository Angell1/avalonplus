#风控策略拦截
# 买入前，需要经过风控系统检测，打分通过
# 1、交易标的选择风控

# 2、交易标地市场风控
# 交易超买
# 贪婪情绪
# 估值

# 3、交易策略风控

import numpy as np
from scipy.stats import norm



# 波动率 (Volatility)
# 波动率衡量资产价格的变化程度。更高的波动率通常意味着更高的风险。
# 计算历史波动率
def CalculateVolatility(data):
    data.set_index('trade_date', inplace=True)

    # 计算每日收益率
    data['Returns'] = data['close'].pct_change()

    # 计算年化波动率
    annual_volatility = data['Returns'].std() * np.sqrt(252)  # 252 代表一年中的交易天数
    print(f"252交易日波动率: {annual_volatility:.2%}")
    annual_volatility = data['Returns'].std() * np.sqrt(66)  # 66 代表3个月的交易天数
    print(f"66交易日波动率: {annual_volatility:.2%}")


#
# 　　用公式表示为：
#
# 　　P(ΔPΔt≤VaR)=a
#
# 　　字母含义如下：
#
# 　　P——资产价值损失小于可能损失上限的概率，即英文的Probability。
#
# 　　ΔP——某一金融资产在一定持有期Δt的价值损失额。
#
# 　　VaR——给定置信水平a下的在险价值，即可能的损失上限。
#
# 　　a——给定的置信水平
#
# 　　VaR从统计的意义上讲，本身是个数字，是指面临“正常”的市场波动时“处于风险状态的价值”。即在给定的置信水平和一定的持有期限内，预期的最大损失量(可以是绝对值，也可以是相对值)。
# 例如，某一投资公司持有的证券组合在未来24小时内，置信度为97.5%，在证券市场正常波动的情况下，VaR值为520万元，其含义是指，该公司的证券组合在一天内(24小时)，由于市场价格变化而带来的最大损失超过520万元的概率为5%，平均20个交易日才可能出现一次这种情况。
# 或者说有95%的把握判断该投资公司在下一个交易日内的损失在520万元以内。5%的几率反映了金融资产管理者的风险厌恶程度，可根据不同的投资者对风险的偏好程度和承受能力来确定。
#  在险价值（VaR）
# 在险价值，一定置信水平下，某交易品种在未来一段时间内可能的最大损失
# 持有周期：在险价值
# 置信水平：99%
# 观察期间：历史数据观察取值一年
def CalculateVaR(data):
    confidence_level = 0.975
    # 计算每日收益率
    data['Returns'] = data['close'].pct_change()
    mean_return = data['Returns'].mean()
    std_return = data['Returns'].std()

    # 基于正态分布计算 VaR
    var_98= norm.ppf(1 - confidence_level, mean_return, std_return) * np.sqrt(252)
    print(f"VaR (98% confidence level): {var_98:.2%}")