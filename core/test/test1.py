import pandas as pd
import adata
import numpy as np
from pyfinance import TSeries
def get_data(code,start='2011-01-01',end=''):
    df=adata.stock.market.get_market_index("000001")
    df.index = pd.to_datetime(df.trade_date)
    print(type(df))
    ret=df.close/df.close.shift(1)-1
    print(type(ret))
    #返回TSeries序列
    return TSeries(ret.dropna()),df

#获取中国平安数据
tss,df=get_data('000001')
#年化收益率
anl_ret=tss.anlzd_ret()
#累计收益率
cum_ret=tss.cuml_ret()
#计算周期收益率
q_ret=tss.rollup('Q')
a_ret=tss.rollup('A')

print(f'年化收益率：{anl_ret*100:.2f}%')
print(f'累计收益率：{cum_ret*100:.2f}%')
print(f'季度收益率：{q_ret.tail().round(4)}')
print(f'历年收益率：{a_ret.round(4)}')
print(df)
