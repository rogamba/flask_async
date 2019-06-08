# -*- coding: utf-8 -*-
"""
    flask_async

    flas-async is a simple flask extension to support asynchronous 
    requests by a simple decorator through the use of celery workers
    :copyright: (c) 2019 by Rodrigo Gamba.
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'flask_cors/version.py'), 'r') as f:
    exec(f.read())

with open (join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name='Flask-Cors',
    version=__version__,
    url='https://github.com/rogamba/flask-async',
    license='MIT',
    author='Rodrigo Gamba',
    author_email='gamba.lavin@gmail.com',
    description="A Flask extension adding a decorator for making async requests",
    packages=['flask-async'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=install_requires
)