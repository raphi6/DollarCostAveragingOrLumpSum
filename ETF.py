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
        print('Annualized:      {:.2f}%'.format(100*(1+self.roi)**(365/(end_date-actual_start).days) -1))
        #print('Annualised: {:.2f}%'.format(100*((1+self.roi)**(365/(end_date-actual_start).days) -1)))
        print('Gross Return:    ${:,.2f}'.format(self.broker.get_value() - self.val_start))

""" What is the fixed commission scheme ? """
class FixedCommissionScheme(bt.CommInfoBase):

    paras = (
        ('commission', 10),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED)
    )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission


def run(data):
    cerebro = bt.Cerebro()                                # The handler of BackTrader (the backbone)
    cerebro.adddata(data)
    cerebro.addstrategy(BuyAndHold)

    # Broker Information
    broker_args = dict(coc=True)                           # coc - cheat on close
    cerebro.broker = bt.brokers.BackBroker(**broker_args)  # To enable coc=True
    comminfo = FixedCommissionScheme()
    cerebro.broker.addcommissioninfo(comminfo)

    cerebro.broker.set_cash(100000)    # How much money we start with

    cerebro.run()

    cerebro.plot(iplot=False, style='candlestick')

if __name__ == '__main__':
    run(data)
