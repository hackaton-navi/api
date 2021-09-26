import urllib.request
import json
import time
from datetime import date, timedelta, datetime
import csv
import pandas as pd
import numpy as np

def get_price(code):
	timestamp_beginning = time.mktime((date.today()-timedelta(days=365)).timetuple())
	url = "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&includeAdjustedClose=true"%(code, int(timestamp_beginning), int(time.time()))
	response = urllib.request.urlopen(url)

	prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

	df = pd.DataFrame([[p["date"], p["value"] if p["value"] != "null" else np.nan] for p in prices], columns=['DATE', code])

	return df

def get_stocks_prices(stocks):
	today = datetime.today().strftime("%Y%m")
	try:
		df = pd.read_csv("./data/%s_stock_prices.csv"%today)
		return df
	except:
		print("Regenerating data")

	stocks_prices = None
	for stock in stocks:
		df = get_price(stock)
		if stocks_prices is None:
			stocks_prices = df
		else:
			stocks_prices = stocks_prices.merge(df, how="inner", on="DATE")

	stocks_prices.to_csv("./data/%s_stock_prices.csv"%today)

	return stocks_prices