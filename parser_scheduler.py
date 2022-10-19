# sample
import random
import time
import schedule
import checker

# Functions setup
def run_checker():
	print("Resources are being checked by checker (if last_checked more than 1h)")
	checker.check_titles()

# Task scheduling

schedule.every(random.randint(10, 20)).seconds.do(run_checker)

# Loop so that the scheduling task
# keeps on running all time.
while True:

	# Checks whether a scheduled task
	# is pending to run or not
	schedule.run_pending()
	time.sleep(random.randint(10, 20))
