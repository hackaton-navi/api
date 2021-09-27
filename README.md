## ESG Monitor - Numbers Doing Trade

# Flask REST-API
The ESG portfolio optimizer api is built using the Flask framework

## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
```
|──────app/
| |────__init__.py
| |────api/
| | |────__init__.py
| | |────cve/
| | |────user/
| | |────oauth/
| |──────config.Development.cfg
| |──────config.Production.cfg
| |──────config.Testing.cfg
| |────dao/
| |────model/
| |────oauth/
| |────util/
|──────run.py
|──────tests/

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

## Reference

Offical Website

- [Flask](http://flask.pocoo.org/)
- [Flask Extension](http://flask.pocoo.org/extensions/)
- [Flask restplus](http://flask-restplus.readthedocs.io/en/stable/)
- [gunicorn](http://gunicorn.org/)
