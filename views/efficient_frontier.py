import pandas as pd
import numpy as np
from scipy.optimize import minimize
import holoviews as hv

class EfficientFrontier:
	def __init__(self, daily_returns, op=1, stocks=[]):
		self.daily_returns = daily_returns
		if op == 1:
			self.get_ret_vol_sr = self.get_ret_vol_sr1
		else:
			self.get_ret_vol_sr = self.get_ret_vol_sr2
		self.stocks = stocks

	def get_ret_vol_sr1(self, weights): 
		weights = np.array(weights)
		ret = np.sum((self.daily_returns.mean()*weights)*252)
		vol = np.sqrt(np.dot(weights.T,np.dot(self.daily_returns.cov()*252, weights)))
		sr = ret/vol
		return np.array([ret,vol,sr])

	def get_ret_vol_sr2(self, weights): 
		weights = np.array(weights)
		ret = np.sum((self.daily_returns.mean()*weights)*252)
		# NEW SHARPE
		# np.sum((daily_returns.mean()*weights)*252)
		vol = np.sqrt(np.dot(weights.T,np.dot(self.daily_returns.cov()*252, weights)))

		esg_df = self.read_esg_data()

		esg_df = esg_df[esg_df["ticker"].isin(self.stocks)]

		avg = np.mean(esg_df["score_value"])
		std = np.std(esg_df["score_value"])

		esg_df["z-score"] = [(i-avg)/std for i in esg_df["score_value"]]
	
		risk_factor = 0.05
		sr = ret/vol + 2*(risk_factor)* np.sum(esg_df["z-score"])
		# NEW SHARPE
		# risk aversion factor ra
		# sr = sqrt(sr*sr + 2 * ra * (esgi - esgU)/std(esgs))
		return np.array([ret,vol,sr])

	def neg_sharpe(self, weights): 
		return self.get_ret_vol_sr(weights)[2] * -1

	def check_sum(self, weights): 
		return np.sum(weights) - 1

	def minimize_volatility(self, weights):
		return  self.get_ret_vol_sr(weights)[1] 


	def read_esg_data(self):
		companies_df = pd.read_csv("./data/companies_br.csv").set_index("company_id")
		esg_df = pd.read_csv("./data/esg_scores_history_br.csv").set_index("company_id")

		#chosen_stocks = ["EMBR3", "ABEV3", "ITUB4", "VALE3", "PETR4"]
		esg_cohort_df = esg_df[(esg_df["aspect"] == "S&P Global ESG Score")]
		
		l = []
		for i in esg_cohort_df.index:
			if i in companies_df.index:
				l.append(companies_df.loc[i]["ticker"])
			else:
				l.append(None)
		esg_cohort_df["ticker"] = l

		return esg_cohort_df

	def efficient_frontier(self, scatter, weights):
		cons = ({'type':'eq','fun': self.check_sum})
		bounds = []
		for i in range(len(weights)):
			bounds.append((0, 1))
		bounds = tuple(bounds)
		opt_results = minimize(self.neg_sharpe,weights, method='SLSQP',bounds=bounds,constraints=cons)
		frontier_y = np.linspace(0.1,0.8,100) 

		frontier_volatility = []

		for possible_return in frontier_y:
			# function for return
			cons = ({'type':'eq','fun': self.check_sum},
					{'type':'eq','fun': lambda w: self.get_ret_vol_sr(w)[0] - possible_return})
			
			result = minimize(self.minimize_volatility,weights, method='SLSQP',bounds=bounds,constraints=cons)
			
			frontier_volatility.append(result['fun'])

		return scatter*hv.Curve((frontier_volatility, frontier_y)).opts(color='green', line_dash='dashed')

