import logging
import datetime
from flask import request, current_app, make_response
from .task import Task
from functools import wraps

logger = logging.getLogger(__name__)


def asynchronize(async_function):
    """ Use for flask routes
    """
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if request.method == 'POST':
                params = request.get_json()
            if request.method == 'GET':
                params = request.args.to_dict()
            # Execute function asynchonously
            celery_task = current_app.async_task.apply_async(args=(async_function,params))
            async_id = celery_task.id
            # Setting initial status
            task = Task(async_id)
            task.progress = 0
            # Set request id in the request global object
            request.async_id = celery_task.id
            return f(*args, **kwargs)
        return wrapped_f
    return wrap


def track_progress(f):
    """ Track and store task progress
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Inject task progress every n lines of code
        # Catch exceptions
        return f(*args, **kwargs)
    return decorated_function



