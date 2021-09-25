from flask import Flask, Response, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
	return "<p>Hello, World!</p>"

def merged_esg_scores():
	companies_df = pd.read_csv("../data/companies_br.csv").set_index("company_id")
	esg_df = pd.read_csv("../data/esg_scores_history_br.csv").set_index("company_id")

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
	ebitda_df = pd.read_csv("../data/ebitda_hist.csv").set_index("ticker")
	for column in ebitda_df.columns:
		ebitda_df[column] = pd.to_numeric(ebitda_df[column])

	return ebitda_df

@app.route("/optimize", methods=["post"])
def stocks():
	data = request.get_json()
	e_cohort = data["e"]
	s_cohort = data["s"]
	g_cohort = data["g"]
	amount_stocks = data["amount"]

	ebitda_df = get_ebitda_df()

	df = merged_esg_scores()
	df = df.loc[(df.parent_aspect == 'S&P Global ESG Score')]

	pivoted_df = df.pivot_table(index='ticker', columns='aspect', values='score_value')
	pivoted_df = pivoted_df.loc[((pivoted_df['Environmental Dimension'] > e_cohort)
             & (pivoted_df['Governance & Economic Dimension'] > g_cohort)
             & (pivoted_df['Social Dimension'] > s_cohort))]

	pivoted_df = pivoted_df.merge(ebitda_df, how="inner", on="ticker")

	columns = pivoted_df.columns
	for i in range(3, len(columns)-1):
		prev_column = columns[i+1]
		column = columns[i]
		pivoted_df[column] = (pivoted_df[column]/pivoted_df[prev_column]) - 1

	pivoted_df["sum"] = 0
	pivoted_df["amount"] = 0
	for i in range(3, len(columns)-1):
		pivoted_df["sum"] += pivoted_df[columns[i]]
		pivoted_df["amount"] += 1

	pivoted_df["avg_ebitda_return"] = pivoted_df["sum"] / pivoted_df["amount"]
	pivoted_df = pivoted_df.drop(columns=pivoted_df.columns[3:-1])

	pivoted_df.columns = ['E', 'G', 'S', "avg_ebitda_return"]

	pivoted_df.sort_values(["avg_ebitda_return"], ascending=[0], inplace=True)

	pivoted_df = pivoted_df.iloc[:amount_stocks]

	pivoted_df.reset_index(inplace=True)

	return Response(pivoted_df.to_json(orient="records"), mimetype='application/json')