from __future__ import absolute_import, unicode_literals

import logging

from celery import task

from wc_utils.wc_utils import get_orders_list

# logging fields
_LOG_FILE = 'wc.log'
# _LOG_FILE = '../wc_utils/wc1.log'
_FILE_MODE = 'a'
_LOGGING_FORMAT = '[[%(asctime)s] [%(name)s] [%(levelname)s]]: %(message)s'
_LOGGING_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_LOGGING_LEVEL = logging.INFO

@task()
def task_number_one():
    import requests
    response = requests.post('http://127.0.0.1:8000/orders/update-orders-api/')