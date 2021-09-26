import pandas as pd
import numpy as np
from scipy.optimize import minimize
import holoviews as hv

class EfficientFrontier:
	def __init__(self, daily_returns):
		self.daily_returns = daily_returns
		print("")

	def get_ret_vol_sr(self, weights): 
		weights = np.array(weights)
		ret = np.sum((self.daily_returns.mean()*weights)*252)
		vol = np.sqrt(np.dot(weights.T,np.dot(self.daily_returns.cov()*252, weights)))
		sr = ret/vol
		return np.array([ret,vol,sr])

	def neg_sharpe(self, weights): 
		return self.get_ret_vol_sr(weights)[2] * -1

	def check_sum(self, weights): 
		return np.sum(weights) - 1

	def minimize_volatility(self, weights):
		return  self.get_ret_vol_sr(weights)[1] 

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

