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
    def update_namelist(self, content):
        #Checking namelist, joins, parts, kicks, nick changes and quits
        if content['type'] == 'NAMELIST':
            self.namelist[content['channel']] = content['message'].translate({ord('&'):'',ord('%'):'',ord('+'):'',ord('@'):''}).split()
            self.update_status(content, self.namelist)
        elif content['type'] == 'JOIN':
            #sometimes, the JOIN message can come before the channel's userlist appears, so the bot will ignore it.
            try:
                self.namelist[content['channel']].append(content['name'])
                if content['name'] == self.master:
                    self.update_status(content)
            except:
                pass
        elif content['type'] == 'PART':
            del self.namelist[content['channel']][self.namelist[content['channel']].index(content['name'])]
            if content['name'] == self.master:
                self.update_status(content, self.namelist)
        elif content['type'] == 'KICK':
            del self.namelist[content['channel']][self.namelist[content['channel']].index(content['name'])]
            if content['name'] == self.master:
                self.update_status(content,self.namelist)
        elif content['type'] == 'NICK':
            for a in self.namelist.keys():
                if content['name'] in self.namelist[a]:
                    del self.namelist[a][self.namelist[a].index(content['name'])]
                    self.namelist[a].append(content['message'])
            if content['name'] == self.master or content['message'] == self.master:
                self.update_status(content)
        #Letting bot delete QUITTED nick from namelist
        elif content['type'] == 'QUIT':
            for a in self.namelist.keys():
                if content['name'] in self.namelist[a]:
                    del self.namelist[a][self.namelist[a].index(content['name'])]
            if content['name'] == self.master:
                self.update_status(content)
    def update_status(self, content, namelist=None):
        if namelist != None:
            #This means that content['type'] is either NAMELIST, PART or KICK
            self.master_online_status = self.check_master_status(namelist)
        elif content['type'] == 'JOIN':
            self.master_online_status = True
        elif content['type'] == 'QUIT':
            self.master_online_status = False
        elif content['type'] == 'NICK':
            #content['name'] is old nick, content['message'] is new
            if content['name'] == self.master:
                self.master_online_status = False
            elif content['message'] == self.master:
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


