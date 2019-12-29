# Basic-Auto-Stock-Trader

#This bot does not implement an API to actually trade (buy/sell) shares in any stock. One could utilize Alpaca API to do this.

#This program assumes you have a budget of $1000 daily to invest in 5 different stocks, with $200 being allocated to each of the 5 stocks.

#The bot will only purchase a stock (out of the top 5 most active stocks on Yahoo Finance) if its current price is below the average of the previous two week's weekly highs.

#This bot will hold the stock until the current price is above the aforementioned weekly average high, and then it will sell it.

#If a stock's current price decreases by more than 10% from the price at which it was initially bought, the bot will immediately sell all shares of the given stock.
