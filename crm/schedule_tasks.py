import schedule
import time


def job():
    import requests
    response = requests.post('http://127.0.0.1:8000/orders/update-orders-api/')


schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
