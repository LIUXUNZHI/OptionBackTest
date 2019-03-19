
from database.data_reader import get_option_data
from database.util import calc_month
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
class DataMgr(object):
    def __init__(self, start_date, end_date):
        """

        :param start_date:
        :param end_date:
        """
        self._raw_data = get_option_data(start_date, end_date)
        self._data = self._raw_data.groupby(by=self._raw_data.index)
    @property
    def data(self):
        return self._data


x = DataMgr('2019-01-01', '2019-04-01')
z = x.data


def find_base_strike(df):
    if len(df) == 0:
        return 0,0
    this_call = df[df.opt_type == 'C']
    this_call = this_call.set_index('opt_strike')
    this_put = df[df.opt_type == 'P']
    this_put = this_put.set_index('opt_strike')
    this_spread = this_call.sort_values(by='opt_strike')['opt_close'] - this_put.sort_values(by='opt_strike')[
        'opt_close']
    strike = abs(this_spread).sort_values().index[0]
    spread = abs(this_spread).sort_values()
    spread = spread.iloc[0]
    return strike, spread


def calc_var(df, strike, future):
    call = df[(df.opt_type == 'C' ) & (df.opt_strike > strike)]
    put = df[(df.opt_type == 'P') & (df.opt_strike < strike)]
    small_k = 0.05
    t = df['expired_days'].iloc[0]
    sigma = 0
    if(range(len(call)) !=0 ):
        for i in range(len(call)):
            sigma += small_k / call['opt_strike'].iloc[i] ** 2 * np.exp(0.03 * t/365) * call['opt_close'].iloc[i]
    if (range(len(put)) != 0):
        for j in range(len(put)):
            sigma += small_k / put['opt_strike'].iloc[j] ** 2 * np.exp(0.03 * t/365) * put['opt_close'].iloc[j]
    sigma = sigma * 2 / (t/365)
    sigma = sigma -1/(t/365) * (future/strike - 1)**2
    return sigma


def calc_vix(var0, var1, t1, t2, n=30):
    part1 = t1/365 * var0 * (t2 - n)/(t2 - t1)
    part2 = t2/365 * var1 * (n - t1)/(t2 - t1)
    return 100 * np.sqrt((part1 + part2) * 365 / n)

id = []
val = []
for i in z:
    opt_tag = i[1].opt_mon[1]
    this_month = i[1].loc[(i[1].exp_mon == opt_tag)]
    next_month = i[1].loc[(i[1].exp_mon == calc_month(1,opt_tag))]
    this_strike, this_spread = find_base_strike(this_month)
    next_strike, next_spread = find_base_strike(next_month)
    if this_strike == 0 or next_strike == 0:
        continue
    this_future = this_strike + np.exp(0.03*this_month.expired_days.iloc[0]/365) * this_spread
    next_future = next_strike + np.exp(0.03*next_month.expired_days.iloc[0]/365) * next_spread
    k_0 = this_month[this_month['opt_strike'] < this_strike]['opt_strike'].max()
    k_1 = next_month[next_month['opt_strike'] < next_strike]['opt_strike'].max()
    if(np.isnan(k_0)):
        k_0 = this_future
    if(np.isnan(k_1)):
        k_1 = next_future
    var0 = calc_var(this_month,k_0,this_future)
    var1 = calc_var(next_month,k_1, next_future)

    t1 = this_month['expired_days'].iloc[0]
    t2 = next_month['expired_days'].iloc[0]
    ivix = calc_vix(var0, var1, t1, t2)
    val.append(ivix)
    id.append(i[0])

x = pd.DataFrame(index=id, data=val)
plt.figure()
x.plot()
plt.show()