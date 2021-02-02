import pandas as pd
import tushare as ts
ts.set_token('834b3d7df208c6eb9387c2d15cba2ff4e2a6c5a2bbe26d4427443df9')
pro = ts.pro_api()
# data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
df = pro.daily(trade_date='20181215', ts_code='600307.SH')
# df = pro.index_daily(ts_code='000001.SZ')
df.to_csv('eee' +'.csv')

# import os
# import tushare as ts
# ts.set_token('834b3d7df208c6eb9387c2d15cba2ff4e2a6c5a2bbe26d4427443df9')
# def ReadTxtName(rootdir):
#     lines = []
#     with open(rootdir, 'r') as file_to_read:
#         while True:
#             line = file_to_read.readline()
#             if not line:
#                 break
#             line = line.strip('\n')
#             lines.append(line)
#     return lines
# stockList = ReadTxtName('20200218A.txt')
# print(stockList,sep=',')
# for stock in stockList:
#     df = ts.get_hist_data(stock)
#     try:
#         df.to_csv(stock+'.csv')
#     except AttributeError:
#         continue
#     print('====================')
