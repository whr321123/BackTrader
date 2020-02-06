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
    
    #Logging function for this strategy
    def log(self,txt,dt=None):
        dt=dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(),txt))
    
    def next(self):
        #Simply log the closing price of the series from the reference.
        self.log('Close, %.2f' % self.dataclose[0])
        
        if self.dataclose[0]<self.dataclose[-1]:
            if self.dataclose[-1]<self.dataclose[-2]:
                
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()
#Main Program
if __name__=='__main__':
    #Initiate Cerebro engine
    cerebro=bt.Cerebro()
    
    #Add a strategy
    cerebro.addstrategy(TestStrategy)
    
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = 'E:\\ForexHistoricalData\\data\\'
    datapath = os.path.join(modpath,'ORCL.csv')
#    print(datapath)
    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2018, 2, 10),
        # Do not pass values after this date
        todate=datetime.datetime(2018, 12, 31),
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    
    
    #Set the beginning balance
    cerebro.broker.setcash(10000.0)
    #Print beginning balance
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    
    #Run cerebro to loop over data    
    cerebro.run()
    #Print final value of the portfolio
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())