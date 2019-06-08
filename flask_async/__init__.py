
# -*- coding: utf-8 -*-
"""
    flask_async

    flas-async is a simple flask extension to support asynchronous 
    requests by a simple decorator through the use of celery workers
    :copyright: (c) 2019 by Rodrigo Gamba.
    :license: MIT, see LICENSE for more details.
"""
from .decorator import asynchronize
from .flask_async import FlaskAsync
from .version import __version__

__all__ = ['FlaskAsync', 'asynchronize']

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

# Set initial level to WARN. Users must manually enable logging for
# flask_cors to see our logging.
rootlogger = logging.getLogger(__name__)
rootlogger.addHandler(NullHandler())

if rootlogger.level == logging.NOTSET:
    rootlogger.setLevel(logging.WARN)
