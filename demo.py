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
        time.sleep(0.2)
        df = self.pro.daily(trade_date=date, ts_code=str(ts_code))
        try:
            ts_code, trade_date, open_price, high, low, close_price, pre_close, change, pct_chg, vol, amount = df.values[0]
            return open_price, close_price, vol
        except Exception as e:
            # print ('No exchange date for [%s] in [%s]' % (ts_code, date))
            return 0, 0, vol

class Stock():

    def __init__(self, ts_code, init_date, amount, price):
        self.id, self.location = ts_code.split('.')
        self.init_date = init_date
        self.total_operation = 1
        self.total_value = 0
        self.amount = amount
        self.price = price
        self.income_flag = True
        self.outgoing_flag = False
        self.realtime_price = 0
        self.last_op_data = ''
        self.clear_flag = False
        self.reason = ''
        self.vol = 0

    def ts_code(self):
        return ('.'.join([self.id, self.location]))

    def add(self, amount, price):
        self.total_operation += 1
        self.total_value += amount * price
        self.amount += amount
        self.price = price
        self.realtime_price = round(self.total_value / self.amount, 3)

    def reduce(self, amount, price):
        self.total_operation -= 1
        self.total_value -= amount * price
        self.amount -= amount
        self.price = price
        if self.amount != 0:
            self.realtime_price = round(self.total_value / self.amount, 3)

    def __repr__(self):
        return ('.'.join([self.id, self.location]))

    def __str__(self):
        return ('.'.join([self.id, self.location]))

def list_check(live_stock, date):
    clear_list = []
    global BASE_DATE
    for stock in live_stock:
        if stock.amount > 0:
            clear_list.append(stock)
        else:
            print('***Stock [%s] has been removed from tracking list***' % stock)
    diff = 5 - len(clear_list)
    if diff > 0:
        for i in range(diff):
            loop_counter = 0
            while True:
                backup_stock = random.choice(stock_symbols)
                # print('Attempt stock [%s]  ' % backup_stock)
                open_price, close_price, vol = ts.get_price(BASE_DATE, backup_stock)
                # print('Parse stock [%s] on [%s]   ' % (backup_stock, BASE_DATE))
                if open_price != 0 and close_price != 0 and close_price > 20:
                    stock = Stock(backup_stock, BASE_DATE, 0, 0)
                    stock.reason = '新加票'
                    clear_list.append(stock)
                    print('Add new stock in tracing list [%s]' % backup_stock)
                    break
                elif open_price != 0 and close_price != 0 and close_price <= 20:
                    # print('Mismatch price < %s, current price %s' % (20, close_price))
                    loop_counter = 0
                    continue
                else:
                    # print('No trade date is available for stock [%s] on certain value [%s]' % (backup_stock, close_price))
                    loop_counter += 1
                    # print('loop_counter>', loop_counter)
                    if loop_counter >= 3:
                        dt_obj = datetime.datetime.strptime(BASE_DATE, '%Y%m%d')
                        delta = datetime.timedelta(days=1)
                        BASE_DATE = dt_obj + delta
                        # print('MID BASE_DATE>>', BASE_DATE)
                        BASE_DATE = BASE_DATE.strftime('%Y%m%d')
                        loop_counter = 0
    return clear_list

ts = Ts_engine()

for i in range(300):

    for stock in live_stock:
        open_price, close_price, vol = ts.get_price(BASE_DATE, stock)
        if open_price != 0 and not stock.clear_flag:
            stock.price = close_price
            if stock.income_flag:
                if money < open_price * 100:
                    stock.income_flag = False
                    continue
                stock.add(100, open_price)
                money -= open_price * 100
                money -= open_price * 100 * 0.0005
                stock.income_flag = False
                stock.last_op_data = BASE_DATE
                # print('Execute ADD OPERATION on [%s] - %s' % (stock.ts_code(), stock.reason))
                stock.reason = ''
            if stock.outgoing_flag:
                stock.reduce(100, open_price)
                money += open_price * 100
                money -= open_price * 100 * 0.0005
                stock.price = open_price
                stock.outgoing_flag = False
                stock.last_op_data = BASE_DATE
                # print('Execute REDUCE OPERATION on [%s] - %s' % (stock.ts_code(), stock.reason))
                stock.reason = ''

            # if (close_price - stock.realtime_price)/stock.realtime_price >= 0.03 and stock.init_date != BASE_DATE:
            #     stock.income_flag = True
            # elif (close_price - stock.realtime_price)/stock.realtime_price <= -0.03 and stock.init_date != BASE_DATE:
            #     stock.outgoing_flag = True

            # Only concern price on each exchange day
            if 0.05 >= (close_price - open_price)/open_price >= 0.03:
                stock.income_flag = True
                stock.reason = '持仓，股价当日上涨3%'
                print('预备加仓，股价当日上涨3 open-%s  close-%s' % (open_price, close_price))
            # elif -0.05 <= (close_price - open_price)/open_price <= -0.03:
            #     stock.outgoing_flag = True
            #     stock.reason = '减仓，股价当日下跌3%但是小于5%'
            elif (close_price - open_price)/open_price < -0.05:
                stock.clear_flag = True
                stock.reason = '斩仓，当日股价下跌5%'
                print('预备斩仓，当日股价下跌5 open-%s  close-%s' % (open_price, close_price))
            elif (stock.realtime_price - close_price)/stock.realtime_price > 0.3:
                stock.clear_flag = True
                stock.reason = '斩仓，盈利30%'
                print('预备斩仓，盈利30 rt_price-%s  close-%s' % (stock.realtime_price, close_price))
            elif (close_price - stock.realtime_price)/stock.realtime_price < -0.03:
                stock.outgoing_flag = True
                stock.reason = '减仓，股价浮亏3'
                print('预备减仓，股价浮亏3  rt_price-%s  cloes-%s' % (stock.realtime_price, close_price))

        elif stock.clear_flag:
            money += open_price * stock.amount
            stock.price = open_price
            stock.amount = 0
            print('Execute CLEAR OPERATION on [%s] - %s' % (stock.ts_code(), stock.reason))

    for i in live_stock:
        print('<%s - %s - %s - %s> ' % (i.ts_code(), i.amount, i.realtime_price, i.price), end='')
    print('')

    live_stock = list_check(live_stock, BASE_DATE)

    dt_obj = datetime.datetime.strptime(BASE_DATE, '%Y%m%d')
    if dt_obj.weekday() == 4:
        delta = datetime.timedelta(days=3)
    else:
        delta = datetime.timedelta(days=1)
    BASE_DATE = dt_obj + delta
    BASE_DATE = BASE_DATE.strftime('%Y%m%d')
    print('MONEY is [%s]  Date is [%s]' % (money, BASE_DATE))

print('FUNCTION DOWN.')
for stock in live_stock:
    money += stock.total_value
    print('Stock [%s] has value: [%s]' % (stock.ts_code(), stock.total_value))

print('You Have [%s] in the end of this loop.'% money)