# Flask Async

A Flask extension for making asynchonous function calls through a simple
decorator

## Pre-requirements

- Redis >= 2.8.4
- Celery >= 4

## Installation

Install the extension with using pip.

```shell
$ pip install -U flask-async
```

### Configuration variables

The following configuration variables must be added to your Flask application in order to make use of the asycnhronize decorator:

```python
# Celery broker and backed
CELERY_BROKER=""
CELERY_HOST=""
CELERY_PORT=""
CELERY_USER= ""
CELERY_PASSWORD=""
CELERY_REDIS_DB=""
# Task backend
REDIS_HOST=""
REDIS_PORT=""
REDIS_PASSWORD=""
REDIS_DB=""
```


## Usage

To use the package some configuration variables need to be passed to the Flask app, as well as previously started a redis server and a celery worker.

### Running Redis Server

If you don't know the redis configuration and setup, I highly recommend to first have a look at [https://redis.io/topics/quickstart]for documentation and tutorials. Once installed you normally start the redis server with:

```shell
$> redis-server
```

### Run Celery Worker

To run the celery worker inside the flask app context, simply execute the following command

```shell
$> flask worker
```

### Asynchronize

First we need to import the FlaskAsync object and pass the flask application
as a parameter:

```python
from flask import Flask
from config import *
from flask_async import FlaskAsync, asynchronize

# Flask app declaration
app = Flask(__name__)
app.config.from_object('config')
FlaskAsync(app)
```

To create an asynchronous endpoint, simply import the **asynchronize** decorator from the flask_async package and pass the function you want to execute asynchronously. The first step would then be defininf the function you will execute asynchronously:

```python
def async_func(task_id, params):
    time.sleep(5)
    a = 1
    b = 2
    return {"data" : a+b, "msg":"OK"}
```

To asynchronize a function call, add de @asynchronize decorator to the endpoint and pass the function you want to call asynchronously as
a parameter:

```python
@app.route('/async')
@asynchronize(async_func)
def async_start():
    return jsonify({
        'status':'ok', 
        'module': 'task',
        'task_id' : request.async_id
    }) 
```

#### Async Task Status

Once the task is running, we can get the status by adding an endpoint which returns the status and the progress of the task:

```python
@app.route('/status/<task_id>')
def async_stats(task_id):
    return jsonify(FlaskAsync.status(task_id))  
```

Finally, once the task is completed, we can get the result of the task by defining an endpoint to get the result:

```python
@app.route('/result/<task_id>')
def async_result(task_id):
    return jsonify(FlaskAsync.result(task_id))  
```

#### Cancel Tasks

Once a task has started, if we want to cancel it we can call the **cancel** method from the FlaskAsync class:

```python
@app.route('/cancel/<task_id>')
def async_cancel(task_id):
    return jsonify(FlaskAsync.cancel(task_id))  
```


