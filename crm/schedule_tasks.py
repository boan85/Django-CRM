import schedule
import time
import requests


def job():
    response = requests.post('http://127.0.0.1:8000/orders/update-orders-api/')


def update_gravity_forms():
    response = requests.post('http://127.0.0.1:8000/gravity-forms/update-gravity-forms/')


schedule.every(1).minutes.do(job)
schedule.every(1).minutes.do(update_gravity_forms)


while True:
    schedule.run_pending()
    time.sleep(1)
