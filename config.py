# -*- coding: utf-8 -*-
import os
import re

__version__ = '0.1'

APP_NAME='falsk_async'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.dirname(os.path.realpath(__file__)) + "/"

# Celery
CELERY_BROKER = os.getenv('CELERY_BROKER', 'redis')
CELERY_HOST = os.getenv("CELERY_HOST", "192.168.99.100")
CELERY_PORT = int(os.getenv("CELERY_PORT", 6379))
CELERY_USER =  os.getenv('CELERY_USER', '')
CELERY_PASSWORD = os.getenv('CELERY_PASSWORD','')
CELERY_REDIS_DB = os.getenv('REDIS_CELERY_DB',0)

# Task backend
REDIS_HOST=os.getenv('REDIS_HOST','192.168.99.100')
REDIS_PORT=int(os.getenv('REDIS_PORT','6379'))
REDIS_PASSWORD=os.getenv('REDIS_PASSWORD','')
REDIS_DB = os.getenv('REDIS_DB',0)
