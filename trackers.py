import threading
import twitter
import ann
import time




class Trackers(threading.Thread):
    def __init__(self, irc, tpl, annpl, master):
        threading.Thread.__init__(self)
        self.irc, self.tpl, self.annpl, self.master = irc, tpl, annpl, master
        self.twitter = twitter.Twitter(self.irc,self.tpl)
        self.ann = ann.ANN(self.irc,self.annpl)
        self.master_online_status = False
    def update_status(self, dict, namelist=None):
        if namelist != None:
            #This means that dict['type'] is either NAMELIST, PART or KICK
            self.master_online_status = self.check_master_status(namelist)
        elif dict['type'] == 'JOIN':
            self.master_online_status = True
        elif dict['type'] == 'QUIT':
            self.master_online_status = False
        elif dict['type'] == 'NICK':
            #dict['name'] is old nick, dict['message'] is new
            if dict['name'] == self.master:
                self.master_online_status = False
            elif dict['message'] == self.master:
                self.master_online_status = True
    def check_master_status(self, namelist):
        #checks if master is online in irc
        found = False
        for channel in namelist.keys():
            if self.master in namelist[channel]:
                found = True
                return found
        return found
    def run(self):
        while True:
            time.sleep(30)
            self.twitter.run()
            self.ann.run()


