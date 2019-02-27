
from pprint import pprint
from wc_utils.wc_utils import get_index_result, wcapi, get_orders_list, get_order, get_reports_list

a = get_index_result()
b = get_orders_list()
c = get_order(123)
d = get_reports_list()
pprint(d)