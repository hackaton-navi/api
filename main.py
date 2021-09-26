from flask import Flask, Response, request
from flask_cors import CORS
import pandas as pd
import os
from services.yfinance import get_stocks_prices

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
	return "<p>Hello, World!</p>"

def merged_esg_scores():
	companies_df = pd.read_csv("./data/companies_br.csv").set_index("company_id")
	esg_df = pd.read_csv("./data/esg_scores_history_br.csv").set_index("company_id")

	l = []
	for i in esg_df.index:
		if i in companies_df.index:
			l.append(companies_df.loc[i]["ticker"])
		else:
			l.append(None)
	esg_df["ticker"] = l
	return esg_df

@app.route("/stocks")
def read_esg_data():

	esg_df = merged_esg_scores()
	esg_individual_scores = esg_df[(esg_df["parent_aspect"] == "S&P Global ESG Score") | (esg_df["aspect"] == "S&P Global ESG Score")]

	pivoted_df = esg_individual_scores.pivot_table(index='ticker', columns='aspect', values='score_value')
	pivoted_df.columns = ['E', 'G', 'score', 'S']
	pivoted_df.reset_index(inplace=True)

	return Response(pivoted_df.to_json(orient="records"), mimetype='application/json')

def get_ebitda_df():
	ebitda_df = pd.read_csv("./data/ebitda_hist.csv").set_index("ticker")
	for column in ebitda_df.columns:
		ebitda_df[column] = pd.to_numeric(ebitda_df[column])

	return ebitda_df

@app.route("/optimize", methods=["post"])
def stocks():
	data = request.get_json()
	e_cohort = int(data["e"])
	s_cohort = int(data["s"])
	g_cohort = int(data["g"])
	amount_stocks = int(data["amount"])

	ebitda_df = get_ebitda_df()

	df = merged_esg_scores()
	df = df.loc[(df["parent_aspect"] == "S&P Global ESG Score") | (df["aspect"] == "S&P Global ESG Score")]

	pivoted_df = df.pivot_table(index='ticker', columns='aspect', values='score_value')
	pivoted_df = pivoted_df.loc[((pivoted_df['Environmental Dimension'] > e_cohort)
             & (pivoted_df['Governance & Economic Dimension'] > g_cohort)
             & (pivoted_df['Social Dimension'] > s_cohort))]

	pivoted_df = pivoted_df.merge(ebitda_df, how="inner", on="ticker")

	columns = pivoted_df.columns
	for i in range(4, len(columns)-1):
		prev_column = columns[i+1]
		column = columns[i]
		pivoted_df[column] = (pivoted_df[column]/pivoted_df[prev_column]) - 1

	pivoted_df["sum"] = 0
	pivoted_df["amount"] = 0
	for i in range(4, len(columns)-1):
		pivoted_df["sum"] += pivoted_df[columns[i]]
		pivoted_df["amount"] += 1

	pivoted_df["avg_ebitda_return"] = pivoted_df["sum"] / pivoted_df["amount"]
	pivoted_df = pivoted_df.drop(columns=pivoted_df.columns[4:-1])

	pivoted_df.columns = ['E', 'G', 'score', 'S', "avg_ebitda_return"]

	pivoted_df.sort_values(["avg_ebitda_return"], ascending=[0], inplace=True)

	if pivoted_df.shape[0] > amount_stocks:
		pivoted_df = pivoted_df.iloc[:amount_stocks]

	pivoted_df.reset_index(inplace=True)

	return Response(pivoted_df.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-ebitda", methods=["post"])
def ranges_ebitda():
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])

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

	high_score = pivoted_df[(pivoted_df["score"] < value3) & (pivoted_df["score"] > value2)]
	medium_score = pivoted_df[(pivoted_df["score"] < value2) & (pivoted_df["score"] > value1)]
	low_score = pivoted_df[(pivoted_df["score"] < value1) & (pivoted_df["score"] > value0)]

	high_grouped = high_score.mean().to_frame().T
	medium_grouped = medium_score.mean().to_frame().T
	low_grouped = low_score.mean().to_frame().T

	high_grouped["portfolio"] = "High Score ESG"
	medium_grouped["portfolio"] = "Medium Score ESG"
	low_grouped["portfolio"] = "Low Score ESG"

	all_portfolios = pd.concat([high_grouped, medium_grouped, low_grouped])

	return Response(all_portfolios.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-stock-price", methods=["post"])
def ranges_stock_price():
	data = request.get_json()
	value0 = int(data["value0"])
	value1 = int(data["value1"])
	value2 = int(data["value2"])
	value3 = int(data["value3"])

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

	high_score = pivoted_df[(pivoted_df["score"] < value3) & (pivoted_df["score"] > value2)]
	medium_score = pivoted_df[(pivoted_df["score"] < value2) & (pivoted_df["score"] > value1)]
	low_score = pivoted_df[(pivoted_df["score"] < value1) & (pivoted_df["score"] > value0)]

	high_grouped = high_score.mean().to_frame().T
	medium_grouped = medium_score.mean().to_frame().T
	low_grouped = low_score.mean().to_frame().T

	high_grouped["portfolio"] = "High Score ESG"
	medium_grouped["portfolio"] = "Medium Score ESG"
	low_grouped["portfolio"] = "Low Score ESG"

	all_portfolios = pd.concat([high_grouped, medium_grouped, low_grouped])

	return Response(all_portfolios.to_json(orient="records"), mimetype='application/json')


if __name__ == "__main__":
	app.run(host=os.environ.get("HOST", "127.0.0.1"), port=os.environ.get("PORT", 5000))
