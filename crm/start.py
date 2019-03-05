
from pprint import pprint

from wc_utils.wc_utils import get_orders_list


orders = get_orders_list()

coupon = {}
if type(orders) is list:
    for i in orders:
        coup = i.get('coupon_lines')
        pprint(coup)
        coupon = {'coupon_code': coup[0].get('code')}
# pprint(b.get('coupon_lines'))
pprint(orders)



