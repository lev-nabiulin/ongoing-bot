import db.sqlite_connector as sqlite_connector
import itertools
from parse_logic import parse_testing


class my_dictionary(dict):
 
  # __init__ function
  def __init__(self):
    self = dict()
 
  # Function to add key:value
  def add(self, key, value):
    self[key] = value

def check_series(sub_dict):
    flat_list = []
    for user in sub_dict:
        flat_list.append(sub_dict[user])
    titles_for_check = [*set(list(itertools.chain.from_iterable(flat_list)))]
    return parse_testing.Parser.new_series(titles_for_check)



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
    print(check_series(sub_dict))
   
check_titles()