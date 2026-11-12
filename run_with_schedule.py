import time
import schedule
from scraper import job

schedule.every(1).hours.do(job)

print("Scheduler démarré, en attente...")
job()

while True:
    schedule.run_pending()
    time.sleep(30)