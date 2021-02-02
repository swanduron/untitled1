import pandas as pd
import tushare as ts
ts.set_token('834b3d7df208c6eb9387c2d15cba2ff4e2a6c5a2bbe26d4427443df9')
pro = ts.pro_api()
# data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
stock = '000004'

df = ts.get_hist_data(stock)
try:
    df.to_csv(stock + '.csv')
except AttributeError:
    pass
print('====================')