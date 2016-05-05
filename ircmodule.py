import threading
import socket
import sys
import queue
import time
import pickle

class IRC(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.server = "irc.rizon.net"       #settings
        self.config = config
        #This is the default channel that the formatter function uses for 'QUIT'
        self.channel = self.config['channels'][0]['name']
        self.botnick = self.config['name']
        self.master = self.config['master']
        self.inputs = queue.Queue()
        self.disconnected = False
    def connect(self):
        a = "USER "+ self.botnick +" "+ self.botnick +" "+ self.botnick +" :" + self.botnick + "\n"
        b = "NICK "+ self.botnick  +"\n"
        c = "PRIVMSG nickserv :identify %s\r\n" %(self.config['password'])

        self.irc.send(a.encode()) #user authentication
        if self.disconnected == True:
            #Use fake nick first
            for a in range(5):
                self.irc.send('NICK dfdfdf\n'.encode())
            #ghost the real nick
            for a in range(5):
                self.irc.send(('PRIVMSG nickserv:ghost %s %s\r\n' %(self.botnick,self.config['password'])).encode())
            for a in range(5):
                #Use real nick
                self.irc.send(b.encode())
                #Identify real nick
                self.irc.send(c.encode())
            for b in range(5):
                #Join channels
                for a in self.config['channels']:
                    self.irc.send(('JOIN %s %s\n' %(a['name'], a['password'])).encode())
            self.disconnected = False
        elif self.disconnected != True:
            #Use nick
            for a in range(5):
                self.irc.send(b.encode())
            #Identify nickserv
            for a in range(5):
                self.irc.send(c.encode())
            for b in range(5):
                #Join channels
                for a in self.config['channels']:
                    self.irc.send(('JOIN %s %s\n' %(a['name'], a['password'])).encode())

    def run(self):
        while True:
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc.connect((self.server, 6667))
            self.connect()
            while True:
                try:
                    text=self.irc.recv(2040).decode()  #receive the text
                except:
                    self.disconnected = True
                    break
                if text:
                    try:
                        print(text)
                    except:
                        pass
                else:
                    self.disconnected = True
                    #time.sleep(15)
                    break
                #using a list because sometimes multiple messages are received at a time when there's a lag
                list = text.split('\r\n')
                for text in list:
                    if not ':' in text:
                        pass
                    elif text.find('PING :') != -1:
                        pong = 'PONG ' + text.split()[1] + '\r\n'
                        self.irc.send(pong.encode())    #returns 'PONG' back to the server (prevents pinging out!)
                    else:
                        formatted_text = self.formatter(text)
                        if not formatted_text['type'] == None:
                            self.inputs.put(formatted_text)
    def send(self, dict):
        if dict is None:
            return
        if not dict['private_messaged']:
            text = str(dict['type'] + ' ' + dict['channel'] + ' :' + dict['message'] + '\r\n')
        elif dict['private_messaged']:
            text = str(dict['type'] + ' ' + dict['name'] + ' :' + dict['message'] + '\r\n')
        self.irc.send(text.encode())
    def formatter(self,rawtext):
        text = rawtext.split(':', 2)
        dict = {}
        try:    #to circumvent the problem of system messages that do not have enough ':'s
            dict['name'] = text[1].split('!')[0]
            dict['message'] = text[2]
        except:
            pass
        dict['private_messaged'] = False
        if 'PRIVMSG' in text[1]:
            dict['type'] = 'PRIVMSG'
            dict['channel'] = text[1].split('PRIVMSG ',1)[1].split(' ',1)[0]
            if not dict['channel'].startswith('#'):
                dict['private_messaged'] = True
        elif 'JOIN' in text[1]:
            dict['type'] = 'JOIN'   #when a person joins a channel, the channel is reflected in text[2], after the ':', hence get channel from dict['message']
            dict['channel'] = text[2]
            dict['message'] = ''
        elif 'QUIT' in text[1]:
            #:SoraSky!~sora@always.online-never.available QUIT :Quit: leaving
            dict['type'] = 'QUIT'
            dict['message'] = ''
            dict['channel'] = self.channel
        elif 'PART' in text[1]:
            dict['type'] = 'PART'
            dict['channel'] = text[1].split('PART ')[1].split(' ')[0]
            dict['name'] = text[1].split('!')[0]
            dict['message'] = ''
        elif 'NICK' in text[1]:
            dict['type'] = 'NICK'   #old name is dict['name'], new name is dict['message']
            dict['channel'] = None
        elif 'KICK' in text[1]:
            #dict['name'] is the guy who was kicked, and the kicker is in the message
            dict['type'] = 'KICK'
            dict['message'] = 'was kicked by %s' %(dict['name'])
            dict['channel'] = text[1].split('KICK ')[1].split(' ')[0]
            dict['name'] = text[1].split('KICK ')[1].split(' ')[1]
            if dict['name'] == self.botnick:
                #:SoraSky!~sora@always.online-never.available KICK #nanodesu kick_me_pls :test
                text = 'JOIN '+dict['channel']+'\n'
                self.irc.send(text.encode())
        elif 'MODE' in text[1]:     #temporary placeholder
            dict['type'] = 'MODE'
            dict['message'] = ''
            dict['name'] = ''
            dict['channel'] = None
        else:
            dict['channel'], dict['type'] = (None,None)
        return dict
