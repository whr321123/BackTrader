# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 20:28:22 2020

@author: wang6000@umn.edu

This is following The "Quickstart Guide" from Backtrader website.


The basics of running this platform:

Create a Strategy

Decide on potential adjustable parameters

Instantiate the Indicators you need in the Strategy

Write down the logic for entering/exiting the market

Tip

Or alternatively:

Prepare some indicators to work as long/short signals
And then

Create a Cerebro Engine

First: Inject the Strategy (or signal-based strategy)
And then:

Load and Inject a Data Feed (once created use cerebro.adddata)

And execute cerebro.run()

For visual feedback use: cerebro.plot()


"""

from __future__ import (absolute_import, division, print_function, unicode_literals)


import datetime
import sys
import os.path
#Import the backtrader platfrom
import backtrader as bt



class TestStrategy(bt.Strategy):
    
    def __init__(self):
        #Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose=self.datas[0].close
        
        #To keep track of pending orders and buy price/comission
        self.order=None
        self.buyprice=None
        self.buycomm=None
    #Logging function for this strategy
    def log(self,txt,dt=None):
        dt=dt or self.datas[0].datetime.date(0)
        print(dt.strftime('%Y-%m-%d')+' '+str(txt))
    
    
    def notify_order(self,order):
        if order.status in [order.Submitted, order.Accepted]:
            #Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been Completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' % (order.executed.price,order.executed.value,order.executed.comm))
                self.buyprice=order.executed.price
                self.buycomm=order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' % (order.executed.price,order.executed.value,order.executed.comm))
                
                
            self.bar_executed=len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        #Write down: no pending order
        self.order=None
    
    def notify_trade(self,trade):
        if not trade.isclosed:
            return
        
        self.log('OPERATION PROFIT, GROSS %.5f, NET %.5f' % (trade.pnl, trade.pnlcomm))
    
    def next(self):
        #Simply log the closing price of the series from the reference.
        self.log('Close, %.5f' % self.dataclose[0])
        
        
        #Check if an order is pending ... if yes, we cannot send a 2nd one.
        if self.order:
            return
        
        #Check if we are in the market
        if not self.position:
            
            # Not yet... we Might Buy if ...
            if self.dataclose[0]<self.dataclose[-1]:
                if self.dataclose[-1]<self.dataclose[-2]:
                
                    self.log('BUY CREATE, %.5f' % self.dataclose[0])
                    self.order=self.buy()
        
        else:
            
            # Already in the market ... we might sell
            if len(self)>=(self.bar_executed+5):
                #Sell,Sell,Sell!!!(with all possible default parameters)
                self.log('SELL CREATE, %.5f' % self.dataclose[0])
                
                #Keep track of the created order to avoid a 2nd order
                self.order=self.sell()
#Main Program
if __name__=='__main__':
    #Initiate Cerebro engine
    cerebro=bt.Cerebro()
    
    #Add a strategy
    cerebro.addstrategy(TestStrategy)
    
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = 'E:\\ForexHistoricalData\\data\\'
    datapath = os.path.join(modpath,'DAT_XLSX_EURUSD_M1_2019.csv')#'ORCL.csv')
#    print(datapath)
    # Create a Data Feed
    
    data=bt.feeds.GenericCSVData(
            dataname=datapath,
            
            fromdate=datetime.datetime(2019,12,1),
            todate=datetime.datetime(2019,12,15),
            
            nullvalue=0.0,
            
            dtformat=('%Y-%m-%d %H:%M'),
#            tmformat=('%H:%M'),
            
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volumn=-1,
            openinterest=-1)
            
##The chunk below is for ORCL.csv data feeds    
#    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
#        # Do not pass values before this date
#        fromdate=datetime.datetime(2018, 2, 10),
#        # Do not pass values after this date
#        todate=datetime.datetime(2018, 12, 31),
#        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    
    
    #Set the beginning balance
    cerebro.broker.setcash(10000.0)
    
    
    #Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)
    
    #Print beginning balance
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    
    #Compress the 1minute data to Daily data
    cerebro.resampledata(data,timeframe=bt.TimeFrame.Days, compression=1440)
    
    #Run cerebro to loop over data    
    cerebro.run()
    #Print final value of the portfolio
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())