import pandas as pd
from .heatmap import merged_esg_scores

def get_ebitda_df():
	ebitda_df = pd.read_csv("./data/ebitda_hist.csv").set_index("ticker")
	for column in ebitda_df.columns:
		ebitda_df[column] = pd.to_numeric(ebitda_df[column])

	return ebitda_df

def get_optimized_df(request):
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
	return pivoted_df

