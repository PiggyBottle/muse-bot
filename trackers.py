import threading
import twitter
import ann
import time




class Trackers(threading.Thread):
    def __init__(self, irc, tpl, annpl):
        threading.Thread.__init__(self)
        self.irc, self.tpl, self.annpl = irc, tpl, annpl
        self.twitter = twitter.Twitter(self.irc,self.tpl)
        self.ann = ann.ANN(self.irc,self.annpl)
        self.namelist = {}
    def update_namelist(self,namelist):
        self.namelist = namelist
    def run(self):
        while True:
            time.sleep(30)
            self.twitter.run()
            self.ann.run()


