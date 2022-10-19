import sqlite_connector

class my_dictionary(dict):
 
  # __init__ function
  def __init__(self):
    self = dict()
 
  # Function to add key:value
  def add(self, key, value):
    self[key] = value

def check_series(title):
    pass

def check_titles():
    subscriptions = sqlite_connector.get_subscriptions()
    # form list of titles to check for each user
    sub_dict = my_dictionary()
    for item in subscriptions:
        user = item[1]
        titles = []
        for sub in subscriptions:
            if sub[1] is user:

                titles.append(sub[2])
        sub_dict.add(user, titles)
    print(sub_dict)
        
check_titles()