from flask import Flask, Response, request
from flask_cors import CORS
import pandas as pd
import json
import os
from views.heatmap import get_esg_data
from views.optimizer import get_optimized_df
from views.ranges import get_ranges_ebitda, get_ranges_stock_price, get_stock_sectors, get_ranges_pe_ratio, get_scatter_alpha
from views.single import get_historical_price, get_ebitda_growth, get_esg_score, get_esg_growth
from views.increase import get_ebitda_esg_corr
from views.portfolio_analytics import get_cum_return_chart, get_sharpe_ratio_chart, get_efficient_frontier, get_correlation_matrix

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
	return "<p>Welcome to Navi's hackaton ESG Monitor</p>"

@app.route("/stocks")
def stocks():
	df = get_esg_data()
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/optimize", methods=["post"])
def optimize():
	df = get_optimized_df(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-ebitda", methods=["post"])
def ranges_ebitda():
	df = get_ranges_ebitda(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-stock-price", methods=["post"])
def ranges_stock_price():
	df = get_ranges_stock_price(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-pe-ratio", methods=["post"])
def ranges_pe_ratio():
	df = get_ranges_pe_ratio(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ranges-scatter-alpha", methods=["post"])
def ranges_scatter_alpha():
	df = get_scatter_alpha(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/historical-price", methods=["post"])
def historical_price():
	df = get_historical_price(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ebitda-growth", methods=["post"])
def ebitda_growth():
	df = get_ebitda_growth(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/esg-growth", methods=["post"])
def esg_growth():
	df = get_esg_growth(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/esg-data", methods=["post"])
def esg_data():
	df = get_esg_score(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/esg-corr")
def esg_corr():
	df = get_ebitda_esg_corr()
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/sectors")
def sectors():
	sectors = get_stock_sectors()
	return Response(sectors.to_json(orient="records"), mimetype='application/json')

@app.route("/cumulative-return", methods=["post"])
def cumulative_return():
	html = get_cum_return_chart(request)
	return Response(html, mimetype='application/html')

@app.route("/sharpe-ratio", methods=["post"])
def sharpe_ratios():
	html = get_sharpe_ratio_chart(request)
	return Response(html, mimetype='application/html')

@app.route("/efficient-frontier", methods=["post"])
def efficient_frontier():
	html = get_efficient_frontier(request)
	return Response(html, mimetype='application/html')

@app.route("/correl-matrix", methods=["post"])
def correl_matrix():
	html = get_correlation_matrix(request)
	return Response(html, mimetype='application/html')

if __name__ == "__main__":
	app.run(host=os.environ.get("HOST", "127.0.0.1"), port=os.environ.get("PORT", 5000))
