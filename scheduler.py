import time
import sched
from web_parser import getProductFromDb
# Create a scheduler object
scheduler = sched.scheduler(time.time, time.sleep)
# Define a function to run the scheduler
def run_scheduler():
    # Schedule the function to run every 30 minutes
    scheduler.enter(10, 1, getProductFromDb, ())
    # Run the scheduler
    scheduler.run()
    # Schedule the function to run again after 30 minutes
    run_scheduler()


