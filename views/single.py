from services.yfinance import get_price
from .optimizer import get_ebitda_df
from .heatmap import esg_data_df
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