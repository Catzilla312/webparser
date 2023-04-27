import time
import sched
from index_parser import getProductFromDb
# Create a scheduler object
scheduler = sched.scheduler(time.time, time.sleep)
# Define a function to run the scheduler
def run_scheduler():
    # Schedule the function to run every 30 minutes
    #in seconds
    scheduler.enter(60, 1, getProductFromDb, ())
    # Run the scheduler
    scheduler.run()
    # Schedule the function to run again after 30 minutes
    run_scheduler()


