import json
from pprint import pprint

import redis

from wc_gravity_forms.wc_gravity_forms_api_client import Client


class GravityFormsUtils(object):

    def __init__(self):
        _HOST = "localhost"
        _PORT = 6379
        _DB = 1

        _GRAVITY_FORMS_URL = "https://devsit-4132.bolt55.servebolt.com/gravityformsapi/"
        _GRAVITY_FORMS_PUBLIC = "bf794e80f7"
        _GRAVITY_FORMS_KEY = "ad0470135c16cb5"
        try:
            # create redis connection
            self.r = redis.StrictRedis(host=_HOST, port=_PORT, db=_DB)
        except (ConnectionRefusedError, redis.exceptions.ConnectionError) as e:
            print(e)
        self.gf = Client(_GRAVITY_FORMS_URL, _GRAVITY_FORMS_PUBLIC, _GRAVITY_FORMS_KEY)

    def update_forms(self):
        forms = self.gf.get_forms_list()
        forms_ids = ['form_id_{}'.format(form.get('id')) for form in forms]
        forms_dict = dict(zip(forms_ids, forms))
        return_result_list = []
        for form_id, form in forms_dict.items():
            form_from_redis = self.r.get(form_id)
            if not form_from_redis:
                print('Write new form with id {} to redis'.format(form_id))
                return_result_list.append({form_id: form})
                form = json.dumps(form, ensure_ascii=False)
                self.r.set(form_id, form)

    def get_forms(self):
        counter = 1
        continue_iteration = True
        forms_list = []
        while continue_iteration:
            form_id = "form_id_{}".format(counter)
            form = self.r.get(form_id)
            if form:
                forms_list.append(json.loads(form.decode('utf-8')))
                counter += 1
            else:
                continue_iteration = False
        return forms_list

    def get_form(self, form_id):
        form = self.r.get("form_id_{}".format(form_id))
        if form:
            return json.loads(form.decode('utf-8'))

    def get_forms_list_for_front_page(self):
        forms = self.get_forms()
        result_list = []
        for form in forms:
            entries_count = len(self.gf.get_form_entries(form.get('id')))
            is_active = form.get('is_active')
            if is_active == 1:
                is_active = True
            else:
                is_active = False
            form_obj = {'title': form.get('title'),
                        'id': form.get('id'),
                        'is_active': is_active,
                        'entries': entries_count}
            result_list.append(form_obj)
        return result_list



