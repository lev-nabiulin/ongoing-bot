import db.sqlite_connector as sqlite_connector
import itertools
from parse_testing import Parser
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    return Parser.new_series(titles_for_check)

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
    # checked_dict = check_series(sub_dict)
    checked_dict = {1: 3, 2: 5, 3: 4, 4: 1, 5: 8, 6: 24, 7: 15, 8: 2}
    if checked_dict:
        # incoming dict = {title.id: title.ep_now, ...}
        # create list of users subscribed to the title with new ep 
        # data = [title.id: (title.ep_now, [users.tg_id, ...])), ...]

        data = my_dictionary()
        for title, ep_now in checked_dict.items():
            user_list = sqlite_connector.get_subscribers_by_title(title)
            title_data = (ep_now, user_list)
            data.add(title, title_data)
        print(data)
        send_notifications(data)
            
    else:
        logger.info('No new episodes.')

def send_notifications(data):
    for title, t_data in data.items():
        print(title, t_data)
        # send notification about new ep for each user
        for user in t_data[1]:
            print(user)


check_titles()