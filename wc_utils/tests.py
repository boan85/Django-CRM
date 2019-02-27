import unittest

import redis
import requests
import woocommerce
from _pytest.compat import NoneType
from woocommerce import API
from wc_utils import get_index_result, _URL, _KEY, _SECRET, _VERSION, _WP_API, _HOST, _PORT, _DB, garbage_collector, \
    set_writing_time, keys_logging, redis_connection_exception


class WoocommerceAPI(unittest.TestCase):
    wcapi = None
    r = None

    def setUp(self):
        self.wcapi = API(
            url=_URL,  # Your store URL
            consumer_key=_KEY,  # Your consumer key
            consumer_secret=_SECRET,  # Your consumer secret
            wp_api=_WP_API,  # Enable the WP REST API integration
            version=_VERSION  # WooCommerce WP REST API version
        )
        self.r = redis.StrictRedis(host=_HOST, port=_PORT, db=_DB)

    def test_api_is_instance(self):
        self.assertIsInstance(self.wcapi, woocommerce.api.API)

    def test_r_is_instance(self):
        self.assertIsInstance(self.r, redis.client.Redis)

    def test_r_connection(self):
        try:
            clients = self.r.client_list()
        except (redis.exceptions.ConnectionError, redis.exceptions.BusyLoadingError) as e:
            error = "Redis connection fails with exceptions: {}".format(e)
            self.fail(error)

    def test_get_index_result_is_instance(self):
        result = get_index_result()
        self.assertIsInstance(result, dict)

    def test_get_index_result_dict_keys_count(self):
        result = get_index_result()
        keys_count = len(result.keys())
        self.assertEqual(keys_count, 69)

    def test_get_index_result_response_is_instance(self):
        response = self.wcapi.get("")
        self.assertIsInstance(response, requests.models.Response)

    def test_get_index_result_response_status_code(self):
        response_status_code = self.wcapi.get("").status_code
        self.assertEqual(response_status_code, 200)

    def test_garbage_collector_is_instance_with_good_key(self):
        result = garbage_collector('index_result')
        self.assertIsInstance(result, (str, NoneType))

    def test_garbage_collector_is_instance_with_bad_key(self):
        result = garbage_collector('fsdfdsfdfd')
        self.assertIsInstance(result, (str, None))

    def test_garbage_collector_is_instance_with_not_string_key(self):
        result = garbage_collector(123)
        self.assertIsInstance(result, (str, None))

    def test_set_writing_time_is_instance_with_good_key(self):
        result = set_writing_time('index_result')
        self.assertIsInstance(result, (str, None))

    def test_set_writing_time_is_instance_with_bad_key(self):
        result = set_writing_time('sdfdsf')
        self.assertIsInstance(result, (str, None))

    def test_set_writing_time_is_instance_with_not_string_key(self):
        result = set_writing_time(123123)
        self.assertIsInstance(result, (str, None))

    def test_keys_logging_is_instance_with_dict(self):
        test_dict = {'1': 1, '2': 2, '3': 3, '4': 4}
        result = keys_logging(test_dict)
        self.assertIsInstance(result, (str, dict))

    def test_keys_logging_is_instance_not_with_dict(self):
        result = keys_logging('dfgdfg')
        self.assertIsInstance(result, (str, dict))


if __name__ == '__main__':
    unittest.main()
