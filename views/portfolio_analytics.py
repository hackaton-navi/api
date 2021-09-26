import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import panel as pn
pn.extension('plotly')
import hvplot.pandas 
from bokeh.plotting import figure, output_file, save
from bokeh.resources import CDN
from bokeh.embed import file_html
from datetime import datetime
from bokeh.io import curdoc
import holoviews as hv
from dateutil import relativedelta
from bokeh.themes import built_in_themes
from .efficient_frontier import EfficientFrontier
import plotly.express as px
from plotly.io import to_html

def get_html(fig):
	hv.renderer('bokeh').theme = 'dark_minimal'
	renderer = hv.renderer("bokeh")
	html = renderer.html(fig)
	return html

def monte_carlo(cov_matrix_annual, daily_returns, data):
	random_arr = np.random.random(len(cov_matrix_annual.index))
	weights = random_arr / np.sum(random_arr)
	weights = weights/np.sum(weights)
	exp_ret = np.sum((daily_returns.mean()*weights)*252)
	exp_vol = np.sqrt(np.dot(weights.T,np.dot(daily_returns.cov()*252, weights)))
	SR = exp_ret/exp_vol

	num_ports = 3000
	all_weights = np.zeros((num_ports, len(data.columns)))
	ret_arr = np.zeros(num_ports)
	vol_arr = np.zeros(num_ports)
	sharpe_arr = np.zeros(num_ports)

	for ind in range(num_ports): 
		# weights 
		weights = np.array(np.random.random(len(data.columns))) 
		weights = weights/np.sum(weights)  

		# save the weights
		all_weights[ind,:] = weights
			
		# expected return 
		ret_arr[ind] = np.sum((daily_returns.mean()*weights)*252)

		# expected volatility 
		vol_arr[ind] = np.sqrt(np.dot(weights.T,np.dot(daily_returns.cov()*252, weights)))

		# Sharpe Ratio 
		sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]

	max_sr_ret = ret_arr[346]
	max_sr_vol = vol_arr[346]

	scatter = hv.Scatter((vol_arr, ret_arr, sharpe_arr), 'Volatility', ['Return', 'Sharpe Ratio'])
	max_sharpe = hv.Scatter([(max_sr_vol,max_sr_ret)])

	scatter.opts(color='Sharpe Ratio', cmap='plasma', width=600, height=400, colorbar=True, padding=0.1) *\
	max_sharpe.opts(color='red', line_color='black', size=10)

	return scatter, max_sharpe, weights

def get_metrics(stocks):
	stocks = [stock + ".SA" for stock in stocks] + ["IBOV"]

	data = pd.read_csv("./data/202109_stock_prices.csv").set_index("DATE")
	ibov_df = pd.read_csv("./data/Ibovespa.csv").set_index("DATA")

	ibov_df.index = [datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d") for x in ibov_df.index]

	l = []
	COUNTER = 0
	for i in data.index:
		if i in ibov_df.index:
			l.append(ibov_df.loc[i]["FECHAMENTO"])
		else:
			l.append(None)

	data["IBOV"] = l
	for i in data.columns:
		data[i] = pd.to_numeric(data[i], downcast="float")
	data = data.drop(data.columns[0], axis=1)

	l = stocks
	data = data[l]
	daily_returns = data.pct_change()
	cum_returns = ((data.pct_change()+1).cumprod())
	correlation = daily_returns.corr()

	portfolio_std = daily_returns.std()

	volatility = daily_returns.std() * np.sqrt(252)
	volatility.sort_values(inplace=True)

	betas = []

	for item in data:
		covariance = daily_returns[item].cov(daily_returns['IBOV'])
		variance = daily_returns['IBOV'].var()
		beta = round(covariance / variance, 2)
		betas.append([item, beta])

	sharpe_ratios = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))

	cov_matrix_annual = daily_returns.cov() * 252

	weights = np.full((len(cov_matrix_annual.index)), (1/len(cov_matrix_annual.index)))
	port_variance = np.dot(weights.T, np.dot(cov_matrix_annual, weights))
	port_volatility = np.sqrt(port_variance)
	portfolioSimpleAnnualReturn = np.sum(daily_returns.mean()*weights) * 252

	percent_var = str(round(port_variance, 2) * 100) + '%'
	percent_vols = str(round(port_volatility, 2) * 100) + '%'
	percent_ret = str(round(portfolioSimpleAnnualReturn, 2)*100)+'%'

	return daily_returns, cum_returns, correlation, \
		portfolio_std, volatility, betas, sharpe_ratios, data, \
			cov_matrix_annual

def get_cum_return_chart(request):
	data = request.get_json()
	stocks = data["stocks"]
	daily_returns, cum_returns, correlation, \
		portfolio_std, volatility, betas, sharpe_ratios, data, cov_matrix_annual = get_metrics(stocks)
	curdoc().theme = 'dark_minimal'
	fig = cum_returns.hvplot.line().opts(legend_position = 'bottom')
	html = get_html(fig)
	return html

def get_heatmap_correlation():
	daily_returns, cum_returns, correlation = get_metrics()

def get_sharpe_ratio_chart(request):
	data = request.get_json()
	stocks = data["stocks"]

	daily_returns, cum_returns, correlation, \
		portfolio_std, volatility, betas, sharpe_ratios, data, cov_matrix_annual = get_metrics(stocks)

	fig = sharpe_ratios.hvplot.bar(figsize=[15,10], title="Sharpe Ratios")
	html = get_html(fig)
	return html

def get_efficient_frontier(request):
	data = request.get_json()
	stocks = data["stocks"]

	daily_returns, cum_returns, correlation, \
		portfolio_std, volatility, betas, sharpe_ratios, data, cov_matrix_annual = get_metrics(stocks)

	scatter, max_sharpe, weights = monte_carlo(cov_matrix_annual, daily_returns, data)

	ef = EfficientFrontier(daily_returns)

	efficient = ef.efficient_frontier(scatter, weights)

	return get_html(efficient)

def get_correlation_matrix(request):
	data = request.get_json()
	stocks = data["stocks"]

	daily_returns, cum_returns, correlation, \
		portfolio_std, volatility, betas, sharpe_ratios, data, cov_matrix_annual = get_metrics(stocks)

	fig = px.imshow(correlation, template="plotly_dark")
	html_ptr = to_html(fig)
	
	return html_ptr
