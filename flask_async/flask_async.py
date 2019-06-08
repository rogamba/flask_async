from flask import current_app
from celery import Celery
from celery.bin import worker
from redis import Redis
from .task import Task
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class FlaskAsync(object):

    def __init__(self, app=None, config={}):
        self.config = app.config
        self.app = app
        if app != None:
            self.init_app(app)

    def init_app(self, app):
        # Config variables for backend and broker
        url_template = 'redis://:{password}@{host}:{port}/{db_number}'
        
        broker_url = url_template.format(
            password='' if 'CELERY_PASSWORD' not in self.config else self.config['CELERY_PASSWORD'],
            host='127.0.0.1' if 'CELERY_HOST' not in self.config else self.config['CELERY_HOST'],
            port='6379' if 'CELERY_PORT' not in self.config else self.config['CELERY_PORT'],
            db_number='0' if 'CELERY_BROKER_DB' not in self.config else self.config['CELERY_BROKER_DB'])
        result_backend_url = url_template.format(
            password='' if 'CELERY_PASSWORD' not in self.config else self.config['CELERY_PASSWORD'],
            host='127.0.0.1' if 'CELERY_HOST' not in self.config else self.config['CELERY_HOST'],
            port='6379' if 'CELERY_PORT' not in self.config else self.config['CELERY_PORT'],
            db_number='0' if 'CELERY_BACKEND_DB' not in self.config else self.config['CELERY_BACKEND_DB'])

        # Connect to celery
        celery_app = Celery(
            __name__, 
            broker=broker_url, 
            backend=result_backend_url
        )

        # Configuration variables, json as default serializer
        celery_app.conf.enable_utc = True
        celery_app.conf.accept_content = ['json','pickle']
        celery_app.conf.result_serializer = 'json'
        celery_app.conf.task_serializer = 'json'

        # Including celery app to flask app
        app.celery_app = celery_app

        # Connect to redis
        app.redis = Redis(
            host=self.config['REDIS_HOST'],
            port=self.config['REDIS_PORT'],
            password=self.config['REDIS_PASSWORD'] or None
        )

        @celery_app.task(bind=True,serializer='pickle')
        def async_task(self, func, params):
            # Fetch Task ID
            task_id = self.request.id
            logger.info('Verifying Task:'+str(task_id))
            logger.info('Received params: {}'.format(params))

            # Get the state
            task = Task(task_id)
            task.progress = 0

            # Execute the passed function
            try:
                result = func(task_id,params)
                print("Got result from task...")
            except TaskError as te:
                logger.error(te)
                task.progress = -1
                revoke(task_id, terminate=True)
                raise Exception("Couldn't complete task...")
            except Exception as e:
                logger.error(e)
                task.progress = -1
                revoke(task_id, terminate=True)
                raise Exception("Couldn't complete task...")

            # Setting result
            task.progress=100
            task.result = result

        @app.cli.command('worker')
        def start_worker():
            celery_app.start(argv=['celery', 'worker', '-l', 'info'])

        app.async_task = async_task


    @staticmethod
    def status(task_id):
        task = Task(task_id)
        return task.status


    @staticmethod
    def result(task_id):
        task = Task(task_id)
        return task.result






