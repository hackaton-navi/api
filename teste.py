import pandas as pd

def read_esg_data():
	companies_df = pd.read_csv("../data/companies_br.csv").set_index("company_id")
	esg_df = pd.read_csv("../data/esg_scores_history_br.csv").set_index("company_id")

	l = []
	for i in esg_df.index:
		if i in companies_df.index:
			l.append(companies_df.loc[i]["ticker"])
		else:
			l.append(None)
	esg_df["ticker"] = l

	esg_individual_scores = esg_df[(esg_df["parent_aspect"] == "S&P Global ESG Score") | (esg_df["aspect"] == "S&P Global ESG Score")]

	pivoted_df = esg_individual_scores.pivot_table(index='ticker', columns='aspect', values='score_value')

	return pivoted_df

print(read_esg_data().head())