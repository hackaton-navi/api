import pandas as pd
from .heatmap import esg_data_df

def ebitda_increase():
	esg_df = pd.read_csv("./data/ebitda_year.csv").rename(columns={
		"Ticker": "ticker",
		"FY2020": 2020,
		"FY2019": 2019,
		"FY2018": 2018,
		"FY2017": 2017,
		"FY2016": 2016,
		"FY2015": 2015,
		"FY2014": 2014,
		"FY2013": 2013
	}).set_index("ticker")

	esg_df = esg_df.astype('float')

	columns = esg_df.columns
	for i in range(len(columns)-1):
		prev_column = columns[i+1]
		column = columns[i]
		esg_df[column] = (esg_df[column]/esg_df[prev_column]) - 1

	esg_df.drop(columns=columns[-1], inplace=True)

	return esg_df

def get_ebitda_esg_corr():
	esg_df = ebitda_increase()
	# esg_increase = esg_data_df(year=None)
	esg_increase = esg_data_df(year=None)

	# esg_increase = esg_increase.pivot_table(values="")

	return esg_increase.reset_index()

