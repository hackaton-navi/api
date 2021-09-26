import pandas as pd

def merged_esg_scores(year=2020):
	companies_df = pd.read_csv("./data/companies_br.csv").set_index("company_id")
	esg_df = pd.read_csv("./data/esg_scores_history_br.csv").set_index("company_id")

	if(year is not None):
		esg_df = esg_df[esg_df["assessment_year"] == year]

	l = []
	for i in esg_df.index:
		if i in companies_df.index:
			l.append(companies_df.loc[i]["ticker"])
		else:
			l.append(None)
	esg_df["ticker"] = l
	return esg_df

def esg_data_df():
	esg_df = merged_esg_scores(2020)
	esg_individual_scores = esg_df[(esg_df["parent_aspect"] == "S&P Global ESG Score") | (esg_df["aspect"] == "S&P Global ESG Score")]

	pivoted_df = esg_individual_scores.pivot_table(index='ticker', columns=['aspect'], values='score_value')

	pivoted_df.columns = ['E', 'G', 'score', 'S']
	return pivoted_df

def get_esg_data():
	df = esg_data_df()
	df.reset_index(inplace=True)
	return df