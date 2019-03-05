
from pprint import pprint

from wc_utils.wc_utils import get_orders_list

# a = get_index_result()
b = get_orders_list()
# c = get_order(547)
# d = get_reports_list()
# pprint(d)
# e = get_sales_report(context='dfdf')
# pprint(e)
# pprint(b)
# for i in b:
#     pprint(i)
coupon = {}
if type(b) is list:
    for i in b:
        coup = i.get('coupon_lines')
        pprint(coup)
        coupon = {'coupon_code': coup[0].get('code')}
# pprint(b.get('coupon_lines'))

pprint(coupon)
pprint(b)