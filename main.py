from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
import datetime as dt
import numpy as np
import math
import yfinance as yf
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/dcs', methods =["GET", "POST"])
def dcs():
    tickers = ["EURUSD=X", "GBPUSD=X", "USDSGD=X", "USDJPY=X", "ETH-USD", "RBLX", "SHOP", "LAND", "DLO", "NU", "BX", "KKR", "SPOT", "ARKK", "XLE", "META", "INTU", "PX"]
    today = date.today()

    def dual_crossover_simulation(ticker, short_ma, long_ma, period, interval, fee):

        min_quotes = yf.download(tickers=ticker, period=period, interval=interval)
        minute = np.arange(1, len(min_quotes) + 1)
        min_quotes['min'] = minute
        min_quotes.drop(columns=['Adj Close', 'Open', 'High', 'Low'], inplace = True)
        min_quotes = min_quotes[['min', 'Close', 'Volume']]
        min_quotes = min_quotes.assign(short_ma = min_quotes['Close'].rolling(short_ma).mean())
        min_quotes = min_quotes.assign(long_ma = min_quotes['Close'].rolling(long_ma).mean())
        min_quotes['signal'] = np.where(min_quotes['short_ma'] > min_quotes['long_ma'], 1, 0)
        min_quotes['asset'] = str(ticker)
        min_quotes['signal_type'] = np.where(min_quotes['short_ma'] > min_quotes['long_ma'], "LONG", "SHORT / OFF")
        min_quotes.dropna(inplace=True)
        min_quotes['return'] = np.log(min_quotes['Close']).diff()
        min_quotes['system_return'] = min_quotes['signal'].shift(1) * min_quotes['return']
        min_quotes['entry'] = min_quotes.signal.diff()
        min_quotes['System'] = np.exp(min_quotes['system_return']).cumprod()
        min_quotes['Buy-and-hold'] = np.exp(min_quotes['return']).cumprod()

        min_quotes['fee_placeholder'] = np.where(min_quotes['entry'] != 0, fee, 0)
        min_quotes['fee'] = min_quotes['fee_placeholder'].shift(1)
        min_quotes['system_return_after_fees'] = min_quotes['system_return']-min_quotes['fee']
        min_quotes['System_net_of_fees'] = np.exp(min_quotes['system_return_after_fees']).cumprod()

        return min_quotes

    def generate_today_positions(tickers):
        dfs = []
        for ticker in tickers:
            df = dual_crossover_simulation(ticker=ticker, short_ma=50, long_ma=200, period="20y", interval="1d", fee=0.07/100)
            dfs.append(df.tail(1))
            final_df = pd.concat(dfs)
        return final_df[['short_ma', 'long_ma', 'asset', 'signal_type']]

    dict_vars = {
        'date_today': datetime.now(),
        'df': generate_today_positions(tickers),
    }

    return render_template("dcs.html", content = dict_vars)





