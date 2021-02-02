import random
import tushare as ts
import datetime
import time

ts.set_token('834b3d7df208c6eb9387c2d15cba2ff4e2a6c5a2bbe26d4427443df9')
pro = ts.pro_api()
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
stock_symbols = []
for x in data.loc[:, 'ts_code']:
    if x.startswith('60') or x.startswith('00'):
        stock_symbols.append(x)
selected_stock = random.sample(stock_symbols, 5)

money = 100000
BASE_DATE = '20181212'
live_stock = []

class Ts_engine():

    def __init__(self):
        ts.set_token('834b3d7df208c6eb9387c2d15cba2ff4e2a6c5a2bbe26d4427443df9')
        self.pro = ts.pro_api()
        self.ts = ts

    def get_price(self, date, ts_code):
        # dt_obj = datetime.datetime.strptime(date, '%Y%m%d')
        # delta = datetime.timedelta(days=1)
        # n_days = dt_obj + delta
        df = self.pro.daily(trade_date=date, ts_code=str(ts_code))
        print('trade_date=',date, '<=>ts_code=',str(ts_code), '<=>date=', date)
        try:
            ts_code, trade_date, open_price, high, low, close_price, pre_close, change, pct_chg, vol, amount = df.values[0]
            return open_price, close_price
        except Exception as e:
            print ('No exchange date for [%s] in [%s]' % (ts_code, date))
            return 0,0

class Stock():

    def __init__(self, ts_code, init_date, amount, price):
        self.id, self.location = ts_code.split('.')
        self.init_date = init_date
        self.total_operation = 1
        self.total_value = amount
        self.amount = amount
        self.price = price
        self.income_flag = True
        self.outgoing_flag = False
        self.last_op_data = ''

    def ts_code(self):
        return ('.'.join([self.id, self.location]))

    def add(self, amount, price):
        self.total_operation += 1
        self.total_value += abs(amount)
        self.amount += amount
        self.price = price

    def reduce(self, amount, price):
        self.total_operation -= 1
        self.total_value += abs(amount)
        self.amount -= amount
        self.price = price

    def __repr__(self):
        return ('.'.join([self.id, self.location]))

    def __str__(self):
        return ('.'.join([self.id, self.location]))

def list_check(live_stock, date):
    global money
    clear_list = []
    for stock in live_stock:
        if stock.amount > 0:
            clear_list.append(stock)
    diff = 5 - len(clear_list)
    if diff > 0:
        for i in range(diff):
            backup_stock = random.choice(stock_symbols)
            open_price, close_price = ts.get_price(BASE_DATE, backup_stock)
            stock = Stock(backup_stock, BASE_DATE, 0, 0)
            # money -= open_price * 100
            clear_list.append(stock)
    return clear_list

ts = Ts_engine()
#
# for stock in selected_stock:
#     open_price, close_price = ts.get_price(BASE_DATE, stock)
#     stock_obj = Stock(stock, BASE_DATE, 100, open_price)
#     money -= open_price * 100
#     live_stock.append(stock)


for i in range(300):
    print(live_stock)
    for stock in live_stock:
        time.sleep(0.5)
        open_price, close_price = ts.get_price(BASE_DATE, stock)
        if open_price != 0:
            if stock.income_flag == True:
                stock.add(100, open_price)
                stock.price = open_price
                money -= open_price * 100
                stock.income_flag = False
                stock.last_op_data = BASE_DATE
            if stock.outgoing_flag == True:
                stock.reduce(100, open_price)
                money += open_price * 100
                stock.price = open_price
                stock.outgoing_flag = False
                stock.last_op_data = BASE_DATE
            if (close_price - stock.price)/stock.price >= 0.03 and stock.init_date != BASE_DATE:
                stock.income_flag = True
            elif (close_price - stock.price)/stock.price <= -0.03 and stock.init_date != BASE_DATE:
                stock.outgoing_flag = True

    dt_obj = datetime.datetime.strptime(BASE_DATE, '%Y%m%d')
    delta = datetime.timedelta(days=1)
    BASE_DATE = dt_obj + delta
    BASE_DATE = BASE_DATE.strftime('%Y%m%d')

    live_stock = list_check(live_stock, date)