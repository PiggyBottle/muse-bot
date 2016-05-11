import threading
import twitter
import ann
import time




class Trackers(threading.Thread):
    def __init__(self, irc, tpl, annpl, master, animetiming):
        threading.Thread.__init__(self)
        self.irc, self.tpl, self.annpl, self.master, self.animetiming = irc, tpl, annpl, master, animetiming
        self.twitter = twitter.Twitter(self.irc,self.tpl)
        self.ann = ann.ANN(self.irc,self.annpl)
        self.master_online_status = False
        self.namelist = {}
    def update_namelist(self, dict):
        #Checking namelist, joins, parts, kicks, nick changes and quits
        if dict['type'] == 'NAMELIST':
            self.namelist[dict['channel']] = dict['message'].translate({ord('&'):'',ord('%'):'',ord('+'):'',ord('@'):''}).split()
            self.update_status(dict, self.namelist)
        elif dict['type'] == 'JOIN':
            #sometimes, the JOIN message can come before the channel's userlist appears, so the bot will ignore it.
            try:
                self.namelist[dict['channel']].append(dict['name'])
                if dict['name'] == self.master:
                    self.update_status(dict)
            except:
                pass
        elif dict['type'] == 'PART':
            del self.namelist[dict['channel']][self.namelist[dict['channel']].index(dict['name'])]
            if dict['name'] == self.master:
                self.update_status(dict, self.namelist)
        elif dict['type'] == 'KICK':
            del self.namelist[dict['channel']][self.namelist[dict['channel']].index(dict['name'])]
            if dict['name'] == self.master:
                self.update_status(dict,self.namelist)
        elif dict['type'] == 'NICK':
            for a in self.namelist.keys():
                if dict['name'] in self.namelist[a]:
                    del self.namelist[a][self.namelist[a].index(dict['name'])]
                    self.namelist[a].append(dict['message'])
            if dict['name'] == self.master or dict['message'] == self.master:
                self.update_status(dict)
        #Letting bot delete QUITTED nick from namelist
        elif dict['type'] == 'QUIT':
            for a in self.namelist.keys():
                if dict['name'] in self.namelist[a]:
                    del self.namelist[a][self.namelist[a].index(dict['name'])]
            if dict['name'] == self.master:
                self.update_status(dict)
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
            self.animetiming.check_website(21600)


