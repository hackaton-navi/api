from .optimizer import get_ebitda_df
from .heatmap import merged_esg_scores
import pandas as pd
from services.yfinance import get_stocks_prices

def get_ranges_ebitda(request):
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])
	metric = data["metric"]

	ebitda_df = get_ebitda_df()
	df = merged_esg_scores()
	df = df.loc[(df["parent_aspect"] == "S&P Global ESG Score") | (df["aspect"] == "S&P Global ESG Score")]
	pivoted_df = df.pivot_table(index='ticker', columns='aspect', values='score_value')
	pivoted_df = pivoted_df.merge(ebitda_df, how="inner", on="ticker")

	columns = pivoted_df.columns
	for i in range(4, len(columns)-1):
		prev_column = columns[i+1]
		column = columns[i]
		pivoted_df[column] = (pivoted_df[column]/pivoted_df[prev_column]) - 1
	
	pivoted_df = pivoted_df.drop(columns=pivoted_df.columns[-1])
	pivoted_df = pivoted_df.rename(columns={"Environmental Dimension": "E", "Governance & Economic Dimension": "G", "Social Dimension": "S", "S&P Global ESG Score": "score"})

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

def get_ranges_stock_price(request):
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])
	metric = data["metric"]

	df = merged_esg_scores()
	df = df.loc[(df["parent_aspect"] == "S&P Global ESG Score") | (df["aspect"] == "S&P Global ESG Score")]
	pivoted_df = df.pivot_table(index='ticker', columns='aspect', values='score_value')

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
