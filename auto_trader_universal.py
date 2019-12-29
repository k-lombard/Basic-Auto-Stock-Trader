"""
This bot does not implement an API to actually trade (buy/sell) shares in any stock. One could utilize Alpaca API to do this.
This program assumes you have a budget of $1000 daily to invest in 5 different stocks, with $200 being allocated to each of the 5 stocks.
The bot will only purchase a stock (out of the top 5 most active stocks on Yahoo Finance) if its current price is below the average of the previous two week's weekly highs.
This bot will hold the stock until the current price is above the aforementioned weekly average high, and then it will sell it.
If a stock's current price decreases by more than 10% from the price at which it was initially bought, the bot will immediately sell all shares of the given stock.
"""
from alpha_vantage.timeseries import TimeSeries
from pprint import pprint
import time
import sys
import logging
import os
import threading
import json
import requests
import multiprocessing
from rtstock.stock import Stock
from yahoo_finance import Share
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Bot Processes")
driver = webdriver.Firefox()
driver.get("https://finance.yahoo.com/most-active/?offset=0&count=100")
ts = TimeSeries(key='YOUR_API_KEY_HERE')


def clock():
    while True:
        stock_update(alist, weekly_high_dict)
        time.sleep(60)


def Weekly_Highs():
    global alist
    alist = []
    for i in range(100):
        element = driver.find_elements_by_xpath("""//*[@id="scr-res-table"]/div[1]/table/tbody/tr[{}]/td[1]/a""".format(i))
        for value in element:
            alist.append(value.text)

    driver.close()
    global blist
    blist = alist[::]
    alist = alist[:5]

    logger.info("Successfully scraped top 5 most active stocks from Yahoo Finance.")
    logger.info(alist)

    dictout = {}
    for item in alist:
        data, metadata = ts.get_weekly(str(item))
        dictout[item] = data
    logger.info("Successfully created a dictionary mapping the 5 stock ids to their respective data sets.")

    logger.info(dictout)
    newlist = []
    for item in dictout:
        for piece in dictout[item]:
            newlist.append(piece)

    newlist = newlist[:2]
    logger.info("Successfully parsed last two weeks from Alpha Vantage function ts.get_weekly.")
    logger.info(newlist)
    global weekly_high_dict
    weekly_high_dict = {}
    for item in alist:
        for piece in newlist:
            if item not in weekly_high_dict:
                weekly_high_dict[item] = float(dictout[item][piece]["2. high"])
            else:
                weekly_high_dict[item] += float(dictout[item][piece]["2. high"])

    logger.info("Successfully mapped the 5 stock ids to their respective combined weekly highs.")

    logger.info(weekly_high_dict)

    for item in weekly_high_dict:
        weekly_high_dict[item] = weekly_high_dict[item] / 2

    logger.info("Successfully mapped the 5 stock ids to their respective average weekly highs.")
    logger.info(weekly_high_dict)


    stock_update(alist, weekly_high_dict)






def stock_update(alist, weekly_high_dict):

    global newdict
    newdict = {}
    num = 0
    while True:
        for item in alist:
            data = ts.get_quote_endpoint(item)
            for piece in data[0]:
                if piece == "05. price":
                    num = data[0][piece]
            newdict[item] = float(num)
        logger.info("Successfully pulled current prices of the 5 stocks.")
        logger.info(newdict)
        return stock_evaluation(weekly_high_dict, newdict)


global boughtlist
boughtlist = []
global initial_price_dict
initial_price_dict = {}
global thenum
thenum = 0
def stock_evaluation(weekly_high_dict, newdict):

    for item in newdict:
        if newdict[item] < weekly_high_dict[item] and item not in boughtlist:
            initial_price_dict[item] = newdict[item]
            logger.info("Buying $200 worth of shares of {} stock.".format(item))
            boughtlist.append(item)
            buy(boughtlist, newdict)
        else:
            continue
        #time.sleep(60)
        stock_update(alist, weekly_high_dict)




def buy(boughtlist, newdict):
    global stockamount
    stockamount = {}
    for item in boughtlist:
        if item not in stockamount:



            #$200 divided by the current price of the stock.
            #Send Alpaca API buy requests here.



            anum = 200 // newdict[item]

            stockamount[item] = anum
        else:
            continue

    logger.info("Successfully bought shares in {} of the 5 stocks.".format(len(stockamount)))
    logger.info(stockamount)



def sell(stockamount, newdict):
    global portfolio
    portfolio = 0.00
    while len(stockamount) != 0:
        for item in stockamount:
            if newdict[item] < (.9 * initial_price_dict[item]):


                #Send Alpaca API sell requests here.


                logger.info("Unloaded {} shares of {} stock at ${} per share.").format(stockamount[item], item, newdict[item])
                portfolio += (int(stockamount[item]) * float(newdict[item]))
                del stockamount[item]

            if newdict[item] > weekly_high_dict[item]:


                #Send Alpaca API sell requests here.


                logger.info("Successfully sold {} shares of {} stock at ${} per share.").format(stockamount[item], item, newdict[item])
                portfolio += (int(stockamount[item]) * float(newdict[item]))
                del stockamount[item]
            else:
                continue
        stock_update(alist, weekly_high_dict)
    if len(stockamount == 0):



        logger.info("After selling off all shares of each stock your final portfolio amount is: ${}".format(portfolio))
        return portfolio






def stocktrader():
    global getdata
    getdata = multiprocessing.Process(target=Weekly_Highs())
    getdata.start()
    getdata.terminate()
    global update
    update = multiprocessing.Process(target=clock())
    update.start()
    update.terminate()
    global sellstocks
    sellstocks = multiprocessing.Process(target=sell(stockamount, newdict))
    sellstocks.start()
    sellstocks.terminate()


stocktrader()
