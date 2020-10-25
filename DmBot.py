from lib.instadm import InstaDM
from time import sleep
import os
import confuse
import random
import csv
import time

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

        self.quotas = Quotas(self.config)
        
class Blacklist(object):
    def __init__(self):
        self.users = []
        if not os.path.exists('data/blacklist.csv'):
            os.mknod('data/blacklist.csv')
            with open("data/blacklist.csv", 'w') as f:
                writer = csv.DictWriter(f, fieldnames=["Username"])
                writer.writeheader()
            f.close()

        with open("data/blacklist.csv", 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.users.append(row)
        f.close()

    def addUser(self, u):
        with open("data/blacklist.csv", 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Username"])
            writer.writerow({'Username': u})
            self.users.append({'Username': u})
        f.close()

    def isBlacklisted(self, u):
        for user in self.users:
            if(user['Username'] == u):
                return True
        return False

class Quotas(object):
    def __init__(self, config):
        self.enabled = config["bot"]["quotas"]["activated"].get(bool)
        if self.enabled:
            self.dayTime = time.time()
            self.totalDmSentDay = 0
            self.totalFollowDay = 0
            self.dmPerDay = config["bot"]["quotas"]["dm_per_day"].get(int)
            self.dmPerHour = config["bot"]["quotas"]["dm_per_hour"].get(int)
            self.followPerDay = config["bot"]["quotas"]["follow_per_day"].get(int)
            self.followPerHour = config["bot"]["quotas"]["follow_per_hour"].get(int)
            self.initTimeQuota()

    def initTimeQuota(self):
        self.timeQuota = time.time()
        self.dmSent = 0
        self.followDone = 0

    def resetDaily(self):
        self.dayTime = time.time()
        self.totalDmSentDay = 0
        self.totalFollowDay = 0

    def checkQuota(self):
        if self.dmSent >= self.dmPerHour or self.followDone >= self.followPerHour:
            if (time.time() - self.timeQuota) < 3600:
                print("Hourly quota reached, sleeping 120 sec...")
                sleep(120)
                self.checkQuota()
            else:
                print("Reset hourly quotas!")
                self.initTimeQuota()

        if self.totalDmSentDay >= self.dmPerDay or self.totalFollowDay >= self.followPerDay:
            if (time.time() - self.dayTime) < 86400:
                print("Daily quota reached, sleeping for one hour...")
                sleep(3600)
                self.checkQuota()
            else:
                print("Reset daily quotas!")
                self.resetDaily()

    def addDm(self):
        self.dmSent += 1
        self.totalDmSentDay += 1
        self.checkQuota()

    def addFollow(self):
        self.followDone += 1
        self.totalFollowDay += 1
        self.checkQuota()

def extractUsersFromCsv():
    csv_file = 'IGExport_plba_food.csv'
    usernames = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            usernames.append(row.get('Username'))
    return usernames

# def fetchUsersFromIG(srcUsername):
    


if __name__ == '__main__':
    # Get config from config.yml
    config = Config()
    usersBlacklist = Blacklist()

    # Recover follower list from srcUser account
    followers = extractUsersFromCsv()

    # Auto login
    insta = InstaDM(username=config.username,
                    password=config.password, headless=config.headlessBrowser)

    # Send message
    if(config.autoDm == True):
        for user in followers:
            if usersBlacklist.isBlacklisted(user) == False:
                messageSend = insta.sendMessage(user=user, message=config.dmTemplates[0])
                if messageSend:
                    print("Dm sent to "+user)
                    usersBlacklist.addUser(user)
                    if config.quotas.enabled:
                        config.quotas.addDm()
                    sleep(random.randint(30, 45))
                else:
                    print("Error durring message sending to "+user+". User blacklisted.")
                    usersBlacklist.addUser(user)


        
