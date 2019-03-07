import json
from pprint import pprint

from wc_gravity_forms.gravity_forms_utils import GravityFormsUtils
from wc_gravity_forms.wc_gravity_forms_api_client import Client

gf_instance = GravityFormsUtils()
gf_instance.update_forms()
# forms_list = gf_instance.get_forms()
# pprint(forms_list)
# pprint(len(forms_list))
# form = gf_instance.get_form(1)
rlist = gf_instance.get_forms_list_for_front_page()
pprint(rlist)

