from .optimizer import get_ebitda_df
from .heatmap import merged_esg_scores
import pandas as pd
import numpy as np
from services.yfinance import get_stocks_prices

def get_stock_sectors():
	companies_df = pd.read_csv("./data/sectors.csv")
	sectors_df = companies_df.groupby('Sector').agg({"Ticker": "nunique"})
	sectors_df.rename(columns={"Ticker": "amount"}, inplace=True)
	return sectors_df.reset_index().rename(columns={"Sector": "industry"})

def get_market_cap():
	companies_market_cap = pd.read_csv("./data/market_cap.csv").set_index("ticker")
	return companies_market_cap

def get_pivoted_df(request):
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])
	metric = data["metric"]
	sector = data["sector"] if "sector" in data else None

	if sector == "Todos":
		sector = None

	mc_cohort1 = int(data["mc_cohort1"]) if "mc_cohort1" in data else None
	mc_cohort2 = int(data["mc_cohort2"]) if "mc_cohort2" in data else None

	df = merged_esg_scores()
	df = df.loc[(df["parent_aspect"] == "S&P Global ESG Score") | (df["aspect"] == "S&P Global ESG Score")]

	if sector is not None:
		sectors_df = pd.read_csv("./data/sectors.csv")
		sectors_df = sectors_df.rename(columns={"Ticker": "ticker", "Sector": "sector"}).set_index("ticker")
		df = df.merge(sectors_df, how="inner", on="ticker")
		df = df.loc[df["sector"] == sector]

	if mc_cohort1 is not None and mc_cohort2 is not None:
		companies_market_cap = get_market_cap()
		df = df.merge(companies_market_cap, how="inner", on="ticker")
		df["market_cap"] = df["market_cap"].rank(pct=True)
		df = df[(df["market_cap"] >= mc_cohort1/100) & (df["market_cap"] <= mc_cohort2/100)]

	pivoted_df = df.pivot_table(index='ticker', columns='aspect', values='score_value')
	return pivoted_df

def separate_portfolios(request, pivoted_df):
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])
	metric = data["metric"]

	high_score = pivoted_df[(pivoted_df[metric] < value3) & (pivoted_df[metric] > value2)]
	medium_score = pivoted_df[(pivoted_df[metric] < value2) & (pivoted_df[metric] > value1)]
	low_score = pivoted_df[(pivoted_df[metric] < value1) & (pivoted_df[metric] > value0)]

	high_grouped = high_score.mean().to_frame().T
	medium_grouped = medium_score.mean().to_frame().T
	low_grouped = low_score.mean().to_frame().T

	high_grouped["portfolio"] = "High Score ESG"
	medium_grouped["portfolio"] = "Medium Score ESG"
	low_grouped["portfolio"] = "Low Score ESG"

	all_portfolios = pd.concat([high_grouped, medium_grouped, low_grouped])

	return all_portfolios

def get_ranges_ebitda(request):
	pivoted_df = get_pivoted_df(request)
	ebitda_df = get_ebitda_df()
	pivoted_df = pivoted_df.merge(ebitda_df, how="inner", on="ticker")

	columns = pivoted_df.columns
	for i in range(4, len(columns)-1):
		prev_column = columns[i+1]
		column = columns[i]
		pivoted_df[column] = (pivoted_df[column]/pivoted_df[prev_column]) - 1
	
	pivoted_df = pivoted_df.drop(columns=pivoted_df.columns[-1])
	pivoted_df = pivoted_df.rename(columns={"Environmental Dimension": "E", "Governance & Economic Dimension": "G", "Social Dimension": "S", "S&P Global ESG Score": "score"})

	if pivoted_df.shape[0] == 0:
		return pd.DataFrame([])

	return separate_portfolios(request, pivoted_df)

def get_ranges_stock_price(request):
	pivoted_df = get_pivoted_df(request)
	prices = get_stocks_prices([stock + ".SA" for stock in pivoted_df.index.tolist()])
	prices["DATE"] = pd.to_datetime(prices["DATE"]).dt.strftime('%Y-%m-%d')
	prices.set_index("DATE", inplace=True)
	prices = prices.astype('float').pct_change().iloc[1:]

	for column in prices.columns:
		prices[column] = (1 + prices[column]).cumprod() - 1 

	prices = prices.T

	prices = prices.reset_index().rename(columns={"index": "ticker"})
	prices["ticker"] = [ticker[:-3] for ticker in prices["ticker"]]
	prices.set_index("ticker")
	
	pivoted_df = pivoted_df.rename(columns={"Environmental Dimension": "E", "Governance & Economic Dimension": "G", "Social Dimension": "S", "S&P Global ESG Score": "score"})
	pivoted_df = pivoted_df.merge(prices, how="inner", on="ticker")

	if pivoted_df.shape[0] == 0:
		return pd.DataFrame([])

	return separate_portfolios(request, pivoted_df)

def get_pe_ratio_df():
	pe_ratio_df = pd.read_csv("./data/pe_ratio.csv").set_index("ticker")
	
	for column in pe_ratio_df.columns:
		pe_ratio_df[column] = pd.to_numeric(pe_ratio_df[column])

	return pe_ratio_df

def get_ranges_pe_ratio(request):
	pivoted_df = get_pivoted_df(request)
	pe_ratio_df = get_pe_ratio_df()
	pivoted_df = pivoted_df.merge(pe_ratio_df, how="inner", on="ticker")

	pivoted_df = pivoted_df.rename(columns={"Environmental Dimension": "E", "Governance & Economic Dimension": "G", "Social Dimension": "S", "S&P Global ESG Score": "score"})

	if pivoted_df.shape[0] == 0:
		return pd.DataFrame([])

	return separate_portfolios(request, pivoted_df)

def get_scatter_alpha(request):
	data = request.get_json()
	metric = data["metric"]

	if metric == "E":
		metric = "delta_e"
	elif metric == "S":
		metric = "delta_s"
	elif metric == "G":
		metric = "delta_g"
	elif metric == "score":
		metric = "delta_esg"

	df = pd.read_csv("./data/eagr.csv").set_index("ticker")
	df["delta_alpha"] = 100*df["delta_alpha"]
	average_e = np.mean(df[metric])
	std_e  = np.std(df[metric])
	df[metric] = df[metric].apply(lambda x: (x-average_e)/std_e if abs((x-average_e)/std_e) <= 1.5 else 0)

	df = df.loc[:, ["assessment_year", metric, "delta_alpha"]]
	df = df.rename(columns={metric: "delta_metric"})

	return df.reset_index()