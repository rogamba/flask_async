# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, g
from config import *
from flask_async import FlaskAsync, asynchronize
import json
import config
import os
import datetime
import time
import logging


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


# Functional Endpoints
@app.route('/')
def main():
    """ Service information endpoint
    """
    return jsonify({
        'service' : 'Flask Async'.format(config.__version__),
        'author' : 'Rodrigo Gamba',
        'date' : datetime.datetime.utcnow()
    })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port='8888',
        debug=True
    )
