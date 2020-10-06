from lib.instadm import InstaDM
from instapy import InstaPy
from time import sleep
import os
import confuse
import random
import csv

class ConfuseConfig(confuse.Configuration):
    def config_dir(self):
        return os.getcwd() + "/config"

class Config(object):
    config = ConfuseConfig('IG_Automation_Bot', __name__)

    def __init__(self):
        self.app_name = self.config['app_name'].get(str)
        self.username = self.config["account"]["username"].get(str)
        self.password = self.config["account"]["password"].get(str)
        self.srcAccount = self.config["users_src"]["src_account"].get(str)
        self.fetchQuantity = self.config["users_src"]["fetch_quantity"].get(int)
        self.autoFollow = self.config["bot"]["auto_follow"].get(bool)
        self.autoDm = self.config["bot"]["auto_dm"].get(bool)
        self.maxDmQuantity = self.config["bot"]["max_dm_quantity"].get(int)
        self.maxFollowQuantity = self.config["bot"]["max_follow_quantity"].get(int)
        self.blacklistInteractedUsers = self.config["bot"]["blacklist_interacted_users"].get(bool)
        self.headlessBrowser = self.config["bot"]["headless_browser"].get(bool)
        self.dmTemplates = self.config["dm_templates"].get(list)
        

def extractUsers():
    csv_file = 'IGExport_plba_food.csv'
    usernames = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            usernames.append(row.get('Username'))
    return usernames


if __name__ == '__main__':
    # Get config from config.yml
    config = Config()

    # Recover follower list from srcUser account
    followers = extractUsers()

    # Auto login
    insta = InstaDM(username=config.username,
                    password=config.password, headless=config.headlessBrowser)

    # Send message
    if(config.autoDm):
        for user in followers:
            insta.sendMessage(user=user, message=config.dmTemplates[0])
            print("Dm sent to "+user)
            sleep(random.randint(45, 60))

        
