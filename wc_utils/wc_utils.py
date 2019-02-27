import datetime
import json

import requests
from woocommerce import API
import redis
import logging

# woocommerce fields
_URL = "https://devsit-4132.bolt55.servebolt.com/"
_KEY = "ck_847f60c58e38c38b9bae6b157259c85f49df5d3c"
_SECRET = "cs_4acf9f59433e220c159ff4568ac5aafa18aaff90"
_VERSION = "wc/v2"
_WP_API = True

# redis fields
_HOST = "localhost"
_PORT = 6379
_DB = 1

# garbage collector fields
_STORE_HOURS = 1
_STORE_DAYS = 1
_STORE_MONTHS = 1
_STORE_YEARS = 1

# logging fields
_LOG_FILE = '../wc_utils/wc.log'
_FILE_MODE = 'a'
_LOGGING_FORMAT = '[[%(asctime)s] [%(name)s] [%(levelname)s]]: %(message)s'
_LOGGING_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_LOGGING_LEVEL = logging.INFO

# create woocommerce api instance
wcapi = API(
    url=_URL,  # Your store URL
    consumer_key=_KEY,  # Your consumer key
    consumer_secret=_SECRET,  # Your consumer secret
    wp_api=_WP_API,  # Enable the WP REST API integration
    version=_VERSION  # WooCommerce WP REST API version
)

# logger settings
logging.basicConfig(filename=_LOG_FILE,
                    filemode=_FILE_MODE,
                    format=_LOGGING_FORMAT,
                    datefmt=_LOGGING_DATEFORMAT,
                    level=_LOGGING_LEVEL)

try:
    # create redis connection
    r = redis.StrictRedis(host=_HOST, port=_PORT, db=_DB)
except (ConnectionRefusedError, redis.exceptions.ConnectionError) as e:
    logging.error("Can not connect to redis with exception: {}".format(e))


def redis_connection_exception(error_text=None):
    """
    Logging error text if have redis.exceptions.BusyLoadingError or redis.exceptions.ConnectionError exception
    :param error_text: if not empty - log this text
    :return:
    """
    def real_redis_connection_exception(function):
        def wrapper(*args, **kwargs):
            try:
                reply = function(*args, **kwargs)
                return reply
            except redis.exceptions.BusyLoadingError:
                if error_text:
                    text_to_log = '{0}{1}'.format(error_text, ' redis.exceptions.BusyLoadingError\n')
                    logging.error(text_to_log)
                else:
                    logging.error("Connection ERROR with redis. redis.exceptions.BusyLoadingError\n")
            except redis.exceptions.ConnectionError:
                if error_text:
                    text_to_log = '{0}{1}'.format(error_text, ' redis.exceptions.ConnectionError\n')
                    logging.error(text_to_log)
                else:
                    logging.error("Connection ERROR with redis. redis.exceptions.ConnectionError\n"
                                  "\tTry to check connection credentials.")

        return wrapper

    return real_redis_connection_exception


@redis_connection_exception(error_text='Can not load key from redis. Check connection please.')
def garbage_collector(key):
    """
    Garbage collector (GC). Checking if info in cache is too old.
    IF it is too old - than clear it from cache.
    If not - than do nothing.
    :param key: key with info in redis, should be string.
    :return: string, if info was cleared, or None if not.
    """
    if isinstance(key, str):
        """
        All keys in redis should have pairs which contains key name and ends with '_datetime'
        GC finds keys with ends with '_datetime' and compare timedelta from this key and datetime.now()
        For comparing using hours.
        """
        # TODO Think how we can to get info from redis with one request, when we getting result from main key.
        date_key = '{}{}'.format(key, '_datetime')
        result = r.get(date_key)
        if result:
            result = json.loads(result.decode('utf-8'))
        else:
            return 'Given key does not exists in cache.'
        now = datetime.datetime.now()
        result_datetime = datetime.datetime(
            year=result.get('year'),
            month=result.get('month'),
            day=result.get('day'),
            hour=result.get('hour'),
            minute=result.get('minute'),
            second=result.get('second')
        )
        if now.hour - result_datetime.hour >= _STORE_HOURS or now.day - result_datetime.day >= _STORE_DAYS \
                or now.month - result_datetime.month >= _STORE_MONTHS or now.year - result_datetime.year >= _STORE_YEARS:
            r.delete(key)
            r.delete(date_key)
            return 'Key {} was cleared from the cache, because it comes too old.\n'.format(key.upper())
        else:
            return None
    else:
        return 'Key should be string!\n'


@redis_connection_exception(error_text='Can not write key to redis. Check connection please.')
def set_writing_time(key):
    """
    During saving info to the cache, need to create additional key with saving time info.
    Garbage collector is using this additional key to clear cache.
    :param key: key with info in redis, should be string.
    :return: string with result status.
    """
    # TODO Think how we can to get info from redis with one request, when we getting result from main key.
    if isinstance(key, str):
        date_key = '{}{}'.format(key, '_datetime')
        now = datetime.datetime.now()
        record_date = {
            'year': now.year,
            'month': now.month,
            'day': now.day,
            'hour': now.hour,
            'minute': now.minute,
            'second': now.second
        }
        record_date = json.dumps(record_date, ensure_ascii=False)
        redis_keys = r.keys()
        if bytes(key.encode('utf-8')) in redis_keys:
            r.set(date_key, record_date)  # write datetime to result
            return 'Writing time info was saved.\n'
        else:
            return 'Given key does not exists.\n'
    else:
        return 'Key time writing ERROR. Key should be a string!\n'


def keys_logging(to_log):
    """
    Checking count of dictionary's keys, or list length.
    If this count, or length less than 10 - than log dict.
    :param to_log: type - dict or list
    :return: dictionary, or list, or string with message
    """
    if isinstance(to_log, dict):
        if len(to_log.keys()) < 10:
            return to_log
        else:
            return "Too big result to log it.\n"
    elif isinstance(to_log, list):
        if len(to_log) <= 5:
            return to_log
        else:
            return "Too big result to log it.\n"
    else:
        return 'Wrong type!\n'


@redis_connection_exception()
def get_index_result(console_logging=False):
    """
    Information about all available endpoints on the site.
    :param console_logging: True - write logs to stdout, if False - does not.
    :return: dict of available endpoints.
    """
    if console_logging:
        logging.getLogger().addHandler(logging.StreamHandler())

    # get index results from redis cache
    index_result = r.get('index_result')
    # If index_result does not exists - than find it using woocommerce API
    if index_result:
        logging.info("Get INDEX API info from cache.")
        # convert bytes to dictionary
        try:
            index_result_dict = json.loads(index_result)
        except TypeError:
            index_result_dict = json.loads(index_result.decode('utf-8'))
        # checking count of dict keys, if their count is not too high - than log result.
        logging.info(keys_logging(index_result_dict))

        # using garbage collector to check if info in cache is too old.
        garbage = garbage_collector('index_result')
        if garbage:
            logging.info(garbage)
        return index_result_dict
    else:
        logging.info("Get index API info from website.")
        # getting index info from website with woocommerce api
        try:
            result = wcapi.get("").json()
        except requests.exceptions.MissingSchema:
            logging.error('Can not connect to website, invalid url: {}'.format(_URL))
            return None
        if result:
            if isinstance(result, dict):
                # getting values only from 'routes' keys, others does not important for us.
                result = result['routes']
                result_to_return = result
                # checking count of dict keys, if their count is not too high - than log result.
                logging.info(keys_logging(result))
                # converting dictionary to string format
                result = json.dumps(result, ensure_ascii=False)
                # write result to redis cache
                r.set('index_result', result)
                # for all info in cache we create key with writing time.
                creating_process = set_writing_time('index_result')
                logging.info("Save INDEX api info to redis cache.")
                if creating_process:
                    logging.info(creating_process)
                return result_to_return
            else:
                logging.error("Wrong type of result. It should be a dictionary.\n")
        else:
            logging.error("Have bad result from request to INDEX api\n")


@redis_connection_exception()
def get_orders_list(console_logging=False):
    """
    Get all orders from cache or via API.
    :param console_logging: True - write logs to stdout, if False - does not.
    :return: list of all orders.
    """
    if console_logging:
        logging.getLogger().addHandler(logging.StreamHandler())
    # get orders list from redis cache
    orders_list = r.get('orders_list')
    # If orders list does not exists - than find it using woocommerce API
    if orders_list:
        logging.info("Get ORDERS LIST info from cache.")
        # convert bytes to dictionary
        try:
            orders_list_dict = json.loads(orders_list)
        except TypeError:
            orders_list_dict = json.loads(orders_list.decode('utf-8'))
        # checking list length, if it is not too high - than log result.
        logging.info(keys_logging(orders_list_dict), '\n')

        # using garbage collector to check if info in cache is too old.
        garbage = garbage_collector('orders_list')
        if garbage:
            logging.info(garbage)
        return orders_list_dict
    else:
        logging.info("Get ORDERS LIST info from website.")
        # getting orders list from website with woocommerce api
        try:
            result = wcapi.get("orders").json()
        except requests.exceptions.MissingSchema:
            logging.error('Can not connect to website, invalid url: {}'.format(_URL))
            return None
        if result:
            if isinstance(result, list):
                # checking list length, if it is not too high - than log result.
                logging.info(keys_logging(result))
                # converting list to string format
                result = json.dumps(result, ensure_ascii=False)
                # write result to redis cache
                r.set('orders_list', result)
                # for all info in cache we create key with writing time.
                creating_process = set_writing_time('orders_list')
                logging.info("Save ORDERS LIST info to redis cache.\n")
                if creating_process:
                    logging.info(creating_process)
                return result
            else:
                logging.exception("Wrong type of result. It should be a list.")
        elif not result:
            logging.error("Response return empty list. There are not any ORDER, or something when wrong.\n")


@redis_connection_exception()
def get_order(order_id='', console_logging=False):
    """
    Get info for order with given id from cache, or via API.
    :param order_id: order's id. Should be a string or integer.
    :param console_logging: True - write logs to stdout, if False - does not.
    :return: dict with order info
    """
    if console_logging:
        logging.getLogger().addHandler(logging.StreamHandler())
    if order_id is not '':
        if type(order_id) is int:
            order_id = str(order_id)
    else:
        logging.error("ORDER ID should not be empty!")
        return None
    # get order from redis cache
    order = r.get('order_{}'.format(order_id))
    order_with_id = 'order_{}'.format(order_id)
    # If order does not exists - than find it using woocommerce API
    if order:
        logging.info("Get ORDER with ID [{}] info from cache.".format(order_id))
        # convert bytes to dictionary
        try:
            order_dict = json.loads(order)
        except TypeError:
            order_dict = json.loads(order.decode('utf-8'))
        # checking count of dict keys, if their count is not too high - than log result.
        logging.info(keys_logging(order_dict))

        # using garbage collector to check if info in cache is too old.
        garbage = garbage_collector(order_with_id)
        if garbage:
            logging.info(garbage)
        return order_dict
    else:
        logging.info("Get ORDER with ID [{}] from website.".format(order_id))
        # getting order from website with woocommerce api
        try:
            result = wcapi.get("orders/{}".format(order_id)).json()
        except requests.exceptions.MissingSchema:
            logging.error('Can not connect to website, invalid url: {}'.format(_URL))
            return None
        if result:
            if isinstance(result, dict):
                result_status = result.get('data', {})
                if result_status.get('status', int) == 404:
                    logging.error("Bad result. Error: {}\n".format(result.get('message', str)))
                    return None
                else:
                    # checking count of dict keys, if their count is not too high - than log result.
                    logging.info(keys_logging(result))
                    # converting dictionary to string format
                    result = json.dumps(result, ensure_ascii=False)
                    # write result to redis cache
                    r.set(order_with_id, result)
                    # for all info in cache we create key with writing time.
                    creating_process = set_writing_time(order_with_id)
                    logging.info("Save ORDER with ID [{}] info to redis cache.".format(order_id))
                    if creating_process:
                        logging.info(creating_process)
                    return result
            else:
                logging.exception("Wrong type of result. It should be a dictionary.\n")
        else:
            logging.exception("Have bad result from request to INDEX api\n")


@redis_connection_exception()
def get_reports_list(console_logging=False):
    if console_logging:
        logging.getLogger().addHandler(logging.StreamHandler())
    # get reports list from redis cache
    reports_list = r.get('reports_list')
    # If reports list does not exists - than find it using woocommerce API
    if reports_list:
        logging.info("Get REPORTS LIST info from cache.")
        # convert bytes to dictionary
        try:
            reports_list_dict = json.loads(reports_list)
        except TypeError:
            reports_list_dict = json.loads(reports_list.decode('utf-8'))
        # checking list length, if it is not too high - than log result.
        logging.info(keys_logging(reports_list_dict))

        # using garbage collector to check if info in cache is too old.
        garbage = garbage_collector('reports_list')
        if garbage:
            logging.info(garbage)
        return reports_list_dict
    else:
        logging.info("Get REPORTS LIST info from website.")
        # getting reports list from website with woocommerce api
        try:
            result = wcapi.get("reports").json()
        except requests.exceptions.MissingSchema:
            logging.error('Can not connect to website, invalid url: {}'.format(_URL))
            return None
        if result:
            if isinstance(result, list):
                return_list = []
                for report in result:
                    description = report.get('description', str)
                    description = description.replace(' ', '_')
                    links = report.get('_links', dict).get('self', list)
                    for link in links:
                        return_list.append({'description': description, 'link': link})
                        # converting list to string format
                        return_list_str = json.dumps(return_list, ensure_ascii=False)
                        # write result to redis cache
                        r.set('reports_list', return_list_str)
                # for all info in cache we create key with writing time.
                creating_process = set_writing_time('reports_list')
                if creating_process:
                    logging.info(creating_process)
                # checking list length, if it is not too high - than log result.
                logging.info(keys_logging(return_list))
                logging.info("Save REPORTS LIST info to redis cache.\n")
                return return_list
            else:
                logging.exception("Wrong type of result. It should be a list.")
        elif not result:
            logging.error("Response return empty list. There are not any REPORT, or something when wrong.\n")