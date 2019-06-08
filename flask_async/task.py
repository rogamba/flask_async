from flask import g, request, current_app
import uuid
import json
import datetime
import importlib
import logging

logger = logging.getLogger(__name__)

class Task(object):
    """ Class for managing asynchronous tasks.
        
        Attributes:
            _task_id (uuid) : task_id to track task
            _name (str) : name to be able to map celery task to internal task
            _result (json): json object with the task result
            _backend (str)
            _ttl (int) : task's result time to live
            _status (dic): dictionaty with status vars
                - progress (float)
                - msg (text)
                - text (text [PENDING, RUNNING, COMPLETED]) 
            _data (dict) : result data
            _result (dict) : dictionary with
                - text (str)
                - data (dict) 
            _status_msg (text)
            _result_msg (text)
    """

    # Dictionary of task stages
    STAGE = {
        1 : 'QUEUED',
        2 : 'RUNNING',
        3 : 'COMPLETED',
        4 : 'CANCELLED',
        0 : 'ERROR'
    }

    def __init__(self, task_id=None):
        """ Pass a task_id, if its empty it assumes it's a new task
        """
        self._backend = 'redis'
        self._status = {}
        self._result = {}
        self._data = {}
        self._ttl =  86400  # One day 
        self._progress = 0
        self._stage = ''
        self._name = ''
        self._status_msg = ''
        self._result_msg = ''
        # If no task_id create new one        
        if not task_id:
            # If new task, generate random uuid
            self._task_id = str(uuid.uuid4())     
        else:
            self._task_id = task_id

    @property
    def task_id(self):
        """ Getter for task_id
        """ 
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        """ Task uuid setter, empty the value of
            the status and the result
        """
        self._status = {}
        self._result = {}
        self._task_id = value
        return self.task_id

    @property
    def progress(self):
        """ Getter for task_id
        """ 
        return self._progress

    @progress.setter
    def progress(self, value):
        """ Task progress value setter,
            while setting the value saves the status
        """
        print("Setting progress... {}".format(value))
        try:
            value = int(value)
            if value < -1 or value > 100:
                raise Exception
        except Exception as e:
            logger.error("Incorrect value format")
            return False

        # Case 0: QUEUED
        if value == 0:
            status = {
                "stage" : self.STAGE[1],
                "msg" : "Task is pending to start",
                "progress" : value
            }

        # Case >0 <100: In Progress
        elif value > 0 and value < 100:
            status = {
                "stage" : self.STAGE[2],
                "msg" : "Task is executing...",
                "progress" : value
            }

        # Case 100: COMPLETED
        elif value >= 100:
            status = {
                "stage" : self.STAGE[3],
                "msg" : "Task completed",
                "progress" : value
            }
        # Case -1: CANCELLED
        elif value == -1:
            status = {
                "stage" : self.STAGE[4],
                "msg" : "Task cancelled",
                "progress" : value
            }

        self.status = status
        return self.progress

    @property
    def status(self):
        """ get status from redis or file and
            set status
        """ 
        if self._backend == 'redis':
            res = current_app.redis.get("task:status:{}".format(self._task_id))
            if res:
                self._status = json.loads(res.decode('utf-8'))
            else:
                self._status = {
                    "stage" : self.STAGE[1],
                    "msg" : "Task is pending to start",
                    "progress" : 0
                }
        elif self._backend == None:
            logger.error("Backend not defined to get result")
        return self._status

    @status.setter
    def status(self, status):
        """ 
            Setter for task status, save the value
            in the given backend (redis)

                @Params:
                    :value (dict)
                
                @Returns:
                    :result (bool)
        """
        props = ['stage','msg','progress']
        if type(status) != dict or (set(props) <= set(status.keys())) != True :
            logger.error("Invalid status for task")
            return False
        if 'stage' in status and status['stage']:
            if type(status['stage']) == str:
                self._stage = status['stage']  
            else:
                self._stage = self.STAGE[status['stage']]
        if 'progress' in status and status['progress']: self._progress = status['progress']
        if 'msg' in status and status['msg']: self._status_msg = status['msg']
        self._status = {
            "task_id" : self._task_id,
            "stage" : self._stage,
            "progress" : self._progress,
            "date" : datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S"),
            "msg" : self._status_msg
        }
        self._save_status()
        return self._status
        
    @property
    def result(self):
        """ 
            Getter for task result, get the value
            from the given backend and set it to the
            variable as well
        """
        if self._backend == 'redis':
            res = current_app.redis.get("task:result:"+self._task_id)
            if res:
                self._result = json.loads(res.decode('utf-8'))
                try:
                    self._data = result['data']
                except:
                    pass
            else:
                self._result = {}
        elif self._backend == None:
            logger.error("Backend not defined to get result")
        return self._result

    @result.setter
    def result(self, value):
        """ 
            Setter for task result, save the value
            in the given backend (redis)
                @Params:
                    :value (dict)
                
                @Returns:
                    :result (bool)
        """
        props = ['data', 'msg']
        if type(value) != dict or (set(props) <= set(value.keys())) != True:
            logger.error("Incorrect result format")
            return False
        if 'data' in value and value['data']: self._data = value['data']
        if 'msg' in value and value['msg']: self._result_msg = value['msg']
        self._result = {
            "task_id" : self._task_id,
            "msg" : self._result_msg,
            "data" : self._data,
            "date" : datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S")
        }
        self._save_result()
        return self._result

    @property
    def name(self):
        """ 
            Getter for task name, get the value
            from the given backend and set it to the
            variable as well
        """
        if self._backend == 'redis':
            print("Getting name from redis" + "task:name:"+self._task_id)
            res = current_app.redis.get("task:name:"+self._task_id)
            if res:
                self._name = res.decode('utf-8')
            else:
                self._name = {}
        elif self._backend == None:
            logger.error("Backend not defined to get name")
        return self._name

    @name.setter
    def name(self, name):
        """ 
            Setter for task result, save the value
            in the given backend (redis)

                @Params:
                    :value (dict)
                
                @Returns:
                    :name (name)
        """
        if type(name) != str:
            logger.error("Malformed name")
            return False
        self._name = name
        self._save_name()
        return self._name


    def _save_name(self):
        """ Save status to redis or to file
        """
        try:
            if self._backend == 'redis':
                # Get status from redis
                current_app.redis.set('task:name:'+self._task_id, self._name, ex=self._ttl )
                logger.debug("Task name stored in "+ 'task:name:'+self._task_id )
                return True
            elif self._backend == None:
                logger.error("No backend defined")
                pass
        except Exception as e:
            logger.error("Could not persist task name, check configuration")
            logger.error(e)
            return False


    def _save_status(self):
        """ Save status to redis or to file
        """
        print("Saving status {}".format(self._status))
        try:
            if self._backend == 'redis':
                # Get status from redis
                current_app.redis.set('task:status:'+self._task_id, json.dumps(self._status), ex=self._ttl )
                logger.debug("Task status stored in "+ 'task:status:'+self._task_id )
                return True
            elif self._backend == None:
                logger.error("No backend defined")
                pass
        except Exception as e:
            logger.error("Could not persist task status, check configuration")
            logger.error(e)
            return False


    def _save_result(self):
        """ Save the result of the task in redis
        """
        if not hasattr(self, '_task_id'):
            logger.error("Can not save result without defining the task_id!")
            return False 
        try:
            if self._backend == 'redis':
                current_app.redis.set("task:result:"+self._task_id, json.dumps(self._result), ex=self._ttl )
                return True
            elif self._backend == None:
                logger.error("No backend defined")
                pass
        except Exception as e:
            logger.error("Something went wrong saving task result")
            logger.error(e)
            return False


    def is_running(self):
        """ Check if task is still running
            @Result
                : bool
        """
        return self.status['progress'] < 100 and self.status['progress'] >= 0


    def error(self, msg="Error"):
        """ Save error status in the running task
        """
        if not hasattr(self, '_task_id'):
            logger.error("Can not set error to an undefined task")
            return False 
        # Set error status
        self.status = {
            "stage" : self.STAGE[4],
            "msg" : msg,
            "progress" : -1
        }
        return True
        