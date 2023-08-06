import backtrader as bt
import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance
yfinance.pdr_override()


# Import data:
def get_data(stocks, start, end):
    stock_data = pdr.get_data_yahoo(stocks, start=start, end=end)
    return stock_data

# Vanguard ETF
stock_list = ['VTS.AX']
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=5000)

stock_data = get_data(stock_list[0], start=start_date, end=end_date)

# Actual start, the index might've only started recently
actual_start = stock_data.index[0]

# Giving pandas dataframe of this form:
data = bt.feeds.PandasData(dataname=stock_data)


class BuyAndHold_More_Fund(bt.Strategy):

    params = dict(
        monthly_cash_invested=1000,
        monthly_range=[5,20]  # How often we want to invest the above: how many times, which days

    )

    def __init__(self):
        self.order = None
        self.total_cost = 0
        self.cost_wo_broker = 0
        self.units = 0
        self.times = 0

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def start(self):
        self.broker.set_fundmode(fundmode=True, fundstartval=100.0)  # We want to only evaluate with what money we have
                                                                     # at that time period.
        self.cash_start = self.broker.get_cash()   # Value we can start trading with
        self.val_start = 100.0

        # Timer
        self.add_timer(
            when=bt.timer.SESSION_START,
            monthdays=[i for i in self.p.monthly_range],
            monthcarry=True        # If bank holiday etc, what do we do.
            #timername='buytimer'
        )

    def notify_timer(self, timer, when, *args):

        self.broker.add_cash(self.p.monthly_cash_invested)

        target_value=self.broker.get_value() + self.p.monthly_cash_invested-10  # Get value of account + money to invest
        self.order_target_value(target=target_value)  # Try get target value amount of shares

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():   # Then we want to log that we bought it for the following cost, commission, size, etc

                self.log(
                    'BUY EXECUTED, Price %.2f, Cost %.2f, Comm %.2f, Size %.0f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size)
                )

                self.units += order.executed.size
                self.total_cost += order.executed.value + order.executed.comm
                self.cost_wo_broker += order.executed.value
                self.times += 1

        # A few more cases:
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            print(order.status, [order.Canceled, order.Margin, order.Rejected])

        self.order = None

    def stop(self):
        """ Calculate actual returns """

        self.roi = (self.broker.get_value() / self.cash_start) - 1   # return on investment
        self.froi = (self.broker.get_fundvalue() - self.val_start)   # fund return on investment

        value = self.datas[0].close * self.units + self.broker.get_cash()  # value in account + cash together
        print('-'*50)
        print("Buy * Buy More")
        print('Time in Market: {:.1f} years'.format((end_date - actual_start).days / 365))
        print('#Times:         {:.0f}'.format(self.times))
        print('Value:         ${:,.2f}'.format(value))
        print('Cost:          ${:,.2f}'.format(self.total_cost))
        print('Gross Return:  ${:,.2f}'.format(value - self.total_cost))
        print('Gross %:        {:.2f}%'.format((value / self.total_cost - 1) * 100))
        print('ROI:            {:.2f}%'.format(100.0 * self.roi))
        print('Fund Value:     {:.2f}%'.format(self.froi))
        print(
            'Annualised:     {:.2f}%'.format(100 * ((1 + self.froi / 100) ** (365 / (end_date - actual_start).days) - 1)
                                             ))
        print('-' * 50)


class BuyAndHold(bt.Strategy):           # Inherit Strategy
    def start(self):
        self.val_start = self.broker.get_cash()   # Value we can start trading with

    def nextstart(self):
        """ We want to buy and hold as much as we can at once """

        size = math.floor( (self.broker.get_cash() - 10 ) / self.data[0]  )  # Max amount of units with that amount of money.
                                                                        # This assumes we can buy at close price, so we
                                                                        # will - 10 for commission.
        self.buy(size=size)

    def stop(self):
        """ Calculate actual returns """

        self.roi = (self.broker.get_value() / self.val_start) - 1  # Getting returns on investment
        print('-'*50)
        print("Buy * Hold")
        print('Starting Value:  ${:,.2f}'.format(self.val_start))
        print('ROI:              {:.2f}%'.format(self.roi * 100.0))
        print('Annualized:      {:.2f}%'.format(100*(1+self.roi)**(365/(end_date-actual_start).days) -1)) # SOMETHING
                                                                                                          # WRONG HERE
        #print('Annualised: {:.2f}%'.format(100*((1+self.roi)**(365/(end_date-actual_start).days) -1)))
        print('Gross Return:    ${:,.2f}'.format(self.broker.get_value() - self.val_start))


class FixedCommissionScheme(bt.CommInfoBase):
    """ What is the fixed commission scheme ? """

    paras = (
        ('commission', 10),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED)
    )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission


def run(data):

    # Buy and Hold
    cerebro = bt.Cerebro()                                # The handler of BackTrader (the backbone)
    cerebro.adddata(data)
    cerebro.addstrategy(BuyAndHold)

    # Broker Information
    broker_args = dict(coc=True)                           # coc - cheat on close
    cerebro.broker = bt.brokers.BackBroker(**broker_args)  # To enable coc=True
    comminfo = FixedCommissionScheme()
    cerebro.broker.addcommissioninfo(comminfo)

    cerebro.broker.set_cash(100000)    # How much money we start with





    # Buy and Buy More
    cerebro1 = bt.Cerebro()                                # The handler of BackTrader (the backbone)
    cerebro1.adddata(data)
    cerebro1.addstrategy(BuyAndHold_More_Fund)

    # Broker Information
    broker_args = dict(coc=True)                           # coc - cheat on close
    cerebro1.broker = bt.brokers.BackBroker(**broker_args)  # To enable coc=True
    comminfo = FixedCommissionScheme()
    cerebro1.broker.addcommissioninfo(comminfo)

    cerebro1.broker.set_cash(1000)    # How much money we start with

    cerebro1.run()
    cerebro.run()

    cerebro.plot(iplot=False, style='candlestick')
    cerebro1.plot(iplot=False, style='candlestick')



if __name__ == '__main__':
    run(data)
