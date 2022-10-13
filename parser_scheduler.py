# sample
import random
import time
import schedule

# Functions setup
def run_parser():
	print("Resources are being checked by parser (if last_checked more than 1h)")

# Task scheduling

schedule.every(random.randint(10, 20)).seconds.do(run_parser)

# Loop so that the scheduling task
# keeps on running all time.
while True:

	# Checks whether a scheduled task
	# is pending to run or not
	schedule.run_pending()
	time.sleep(random.randint(10, 20))
