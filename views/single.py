from services.yfinance import get_price
from .optimizer import get_ebitda_df
from .heatmap import esg_data_df, merged_esg_scores
import pandas as pd


def get_esg_score(request):
	data = request.get_json()
	ticker = data["ticker"]
	esg_df = esg_data_df()

	single_esg = esg_df.loc[ticker, :]

	companies_df = pd.read_csv("./data/companies_br.csv").set_index("company_id")
	single_company = companies_df.set_index("ticker").loc[ticker]

	single_esg = single_esg.to_frame().T.reset_index().rename(columns={"index": "ticker"})
	single_company = single_company.to_frame().T.reset_index().rename(columns={"index": "ticker"})

	single_esg = single_esg.merge(single_company, how="inner", on="ticker")

	return single_esg

def get_historical_price(request):
	data = request.get_json()
	ticker = data["ticker"]
	df = get_price(ticker+".SA")
	df.iloc[:, 1:] = df.iloc[:, 1:].astype(float)
	df["DATE"] = pd.to_datetime(df["DATE"]).dt.strftime("%Y-%m-%d")
	
	return df

def get_ebitda_growth(request):
	data = request.get_json()
	ticker = data["ticker"]

	ebitda_df = get_ebitda_df()
	single_stock_ebtida = ebitda_df.loc[ticker, :]

	return single_stock_ebtida.reset_index().rename(columns={"index": "DATE"})


def get_esg_growth(request):
	data = request.get_json()
	ticker = data["ticker"]

	esg_df = merged_esg_scores(None)
	esg_individual_scores = esg_df[(esg_df["parent_aspect"] == "S&P Global ESG Score") | (esg_df["aspect"] == "S&P Global ESG Score")]

	esg_individual_scores = esg_individual_scores[esg_individual_scores["ticker"] == ticker]

	pivoted_df = esg_individual_scores.pivot_table(index='ticker', columns=['aspect', 'assessment_year'], values='score_value')

	e = ["Environmental Dimension", "Environmental"]
	s = ["Social Dimension", "Social"]
	g = ["Governance & Economic Dimension", "Governance"]
	score = ["S&P Global ESG Score", "ESG Score"]

	dfs = []

	dimensions=[e, s, g, score]
	for dimension in dimensions:
		dimension_df = pivoted_df[dimension[0]]
		dimension_df["metric"] = dimension[1]
		dfs.append(dimension_df)

	all_portfolios = pd.concat(dfs)

	for i in range(len(all_portfolios.columns)-2, 0, -1):
		prev_column = all_portfolios.columns[i-1]
		column = all_portfolios.columns[i]

		all_portfolios[column] = (all_portfolios[column]/all_portfolios[prev_column]) - 1

	all_portfolios.drop(columns=[all_portfolios.columns[0]], inplace=True)

	return all_portfolios.reset_index()
