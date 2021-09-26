from flask import Flask, Response, request
from flask_cors import CORS
import pandas as pd
import os
from services.yfinance import get_stocks_prices
from views.heatmap import get_esg_data
from views.optimizer import get_optimized_df
from views.ranges import get_ranges_ebitda, get_ranges_stock_price
from views.single import get_historical_price, get_ebitda_growth, get_esg_score

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

@app.route("/historical-price", methods=["post"])
def historical_price():
	df = get_historical_price(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/ebitda-growth", methods=["post"])
def ebitda_growth():
	df = get_ebitda_growth(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

@app.route("/esg-data", methods=["post"])
def esg_data():
	df = get_esg_score(request)
	return Response(df.to_json(orient="records"), mimetype='application/json')

if __name__ == "__main__":
	app.run(host=os.environ.get("HOST", "127.0.0.1"), port=os.environ.get("PORT", 5000))
