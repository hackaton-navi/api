## ESG Monitor - Numbers Doing Trade

# Flask REST-API
The ESG portfolio optimizer api is built using the Flask framework

- [navi.viniciusbaca.com](http://navi.viniciusbaca.com/)

## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
```
├── custom_filename.html
├── data
│   ├── 202109_stock_prices.csv
│   ├── companies_br.csv
│   ├── eagr.csv
│   ├── ebitda_hist.csv
│   ├── ebitda_year.csv
│   ├── esg_scores_history_br.csv
│   ├── Ibovespa.csv
│   ├── market_cap.csv
│   ├── pe_ratio.csv
│   └── sectors.csv
├── hv_scatter.html
├── main.py
├── Procfile
├── requirements.txt
├── run.sh
├── services
│   └── yfinance.py
├── teste.py
└── views
    ├── efficient_frontier.py
    ├── heatmap.py
    ├── increase.py
    ├── optimizer.py
    ├── portfolio_analytics.py
    ├── ranges.py
    └── single.py

```


## Flask Configuration

#### Example

```
app = Flask(__name__)
app.config['DEBUG'] = True
```
### Configuring From Files

#### Example Usage

```
app = Flask(__name__ )
app.config.from_pyfile('config.Development.cfg')
```



 
## Run Flask
### Run flask for develop
```
$ python webapp/run.py
```

### Run flask for production

** Run with gunicorn **

In  root dir

```
$ gunicorn main:app --bind 0.0.0.0:${PORT}

```

* -w : number of worker
* -b : Socket to bind

## Authors

- Enrico Robazza
- Érico Faustino
- Luca Bottino
- Vinícius Baca

## Reference

Offical Website

- [Flask](http://flask.pocoo.org/)
- [Flask Extension](http://flask.pocoo.org/extensions/)
- [Flask restplus](http://flask-restplus.readthedocs.io/en/stable/)
- [gunicorn](http://gunicorn.org/)
