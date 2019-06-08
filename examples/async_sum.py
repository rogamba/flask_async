# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, g
from config import *
import json
import config
import os
import datetime
import time
import logging
try:
    # The typical way to import flask-async
    from flask_async import FlaskAsync, asynchronize  
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)
    from flask_async import FlaskAsync, asynchronize

# Flask app declaration
app = Flask(__name__)
app.config.from_object('config')
FlaskAsync(app)
logger = logging.getLogger(__name__)

def test_async_func(task_id, params):
    time.sleep(5)
    a = 1
    b = 2
    return {"data" : a+b, "msg":"OK"}

@app.route('/async')
@asynchronize(test_async_func)
def async_start():
    return jsonify({
        'status':'ok', 
        'module': 'task',
        'task_id' : request.async_id
    })    


@app.route('/status/<task_id>')
def async_stats(task_id):
    return jsonify(FlaskAsync.status(task_id))      


@app.route('/result/<task_id>')
def async_result(task_id):
    return jsonify(FlaskAsync.result(task_id))


@app.route('/cancel/<task_id>')
def async_cancel(task_id):
    return jsonify(FlaskAsync.cancel(task_id))


@app.route('/')
def main():
    """ Service information endpoint
    """
    return jsonify({
        'service' : 'Flask Async',
        'author' : 'Rodrigo Gamba',
    })


if __name__ == '__main__':
    app.run(debug=True)
