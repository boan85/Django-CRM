import schedule
import time

from wc_gravity_forms.gravity_forms_utils import GravityFormsUtils


def job():
    import requests
    response = requests.post('http://127.0.0.1:8000/orders/update-orders-api/')


def update_gravity_forms():
    gf_instance = GravityFormsUtils()
    gf_instance.update_forms()


schedule.every(1).minutes.do(job)
schedule.every(1).minutes.do(update_gravity_forms)


while True:
    schedule.run_pending()
    time.sleep(1)
