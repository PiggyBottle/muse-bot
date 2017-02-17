import threading
import socket
import sys
import queue
import time
import pickle
import re

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
            count = 0
            while True:
                decode_success = False
                try:
                    text=self.irc.recv(2040)  #receive the text
                    if count < 4:
                        c = "PRIVMSG nickserv :identify %s\r\n" %(self.config['password'])
                        self.irc.send(c.encode())
                        for a in self.config['channels']:
                            self.irc.send(('JOIN %s %s\n' %(a['name'], a['password'])).encode())
                        count += 1
                except:
                    self.disconnected = True
                    break
                try:
                    text = text.decode()
                    decode_success = True
                except:
                    pass
                if not decode_success:
                    try:
                        text = text.decode('latin-1')
                        decode_success = True
                    except:
                        text = ':Decode Failure\r\n'
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
                        formatted_text = self.formatter1(text)
                        if not formatted_text['type'] == None:
                            self.inputs.put(formatted_text)
    def send(self, content):
        if content is None:
            return
        if not content['private_messaged']:
            text = str(content['type'] + ' ' + content['channel'] + ' :' + content['message'] + '\r\n')
        elif content['private_messaged']:
            text = str(content['type'] + ' ' + content['name'] + ' :' + content['message'] + '\r\n')
        self.irc.send(text.encode())
    def formatter(self,rawtext):
        text = rawtext.split(':', 2)
        content = {}
        try:    #to circumvent the problem of system messages that do not have enough ':'s
            content['name'] = text[1].split('!')[0]
            content['message'] = text[2]
        except:
            pass
        content['private_messaged'] = False
        if 'PRIVMSG' in text[1]:
            content['type'] = 'PRIVMSG'
            content['channel'] = text[1].split('PRIVMSG ',1)[1].split(' ',1)[0]
            if not content['channel'].startswith('#'):
                content['private_messaged'] = True
        elif 'JOIN' in text[1]:
            content['type'] = 'JOIN'   #when a person joins a channel, the channel is reflected in text[2], after the ':', hence get channel from content['message']
            content['channel'] = text[2]
            content['message'] = ''
        elif 'QUIT' in text[1]:
            #:SoraSky!~sora@always.online-never.available QUIT :Quit: leaving
            content['type'] = 'QUIT'
            content['message'] = ''
            content['channel'] = self.channel
        elif 'PART' in text[1]:
            content['type'] = 'PART'
            content['channel'] = text[1].split('PART ')[1].split(' ')[0]
            content['name'] = text[1].split('!')[0]
            content['message'] = ''
        elif 'NICK' in text[1]:
            content['type'] = 'NICK'   #old name is content['name'], new name is content['message']
            content['channel'] = None
        elif 'KICK' in text[1]:
            #content['name'] is the guy who was kicked, and the kicker is in the message
            content['type'] = 'KICK'
            content['message'] = 'was kicked by %s' %(content['name'])
            content['channel'] = text[1].split('KICK ')[1].split(' ')[0]
            content['name'] = text[1].split('KICK ')[1].split(' ')[1]
            if content['name'] == self.botnick:
                #:SoraSky!~sora@always.online-never.available KICK #nanodesu kick_me_pls :test
                text = 'JOIN '+content['channel']+'\n'
                self.irc.send(text.encode())
        elif 'MODE' in text[1]:     #temporary placeholder
            content['type'] = 'MODE'
            content['message'] = ''
            content['name'] = ''
            content['channel'] = None
        elif '353' in text[1]:
            #There are cases where incomplete messages come in and break the bot, so forcing a try-except function
            try:
                if text[1].split()[1] == '353':
                    content['type'] = 'NAMELIST'
                    content['channel'] = text[1].split()[4]
                    content['message'] = text[2]
                    content['name'] = ''
                    #private message was used to make sure it doesn't get logged
                    content['private_messaged'] = True
            except:
                pass
        else:
            content['channel'], content['type'] = (None,None)
        return content
    def formatter1(self,text):
        content = {'private_messaged':False}
        #https://regex101.com/r/hF9mD0/2
        expression = '^:(.*?)((!.*?@(.*?)\s(((PRIVMSG)\s(.*?)\s:(.*))|((QUIT)\s:)|((PART)\s(#\S*))|((NICK)\s:(.*))|((KICK)\s(#.*?)\s(.*?)\s:)|((JOIN)\s:(#.*))))|(\s(353)\s.*?\s.\s(#.*?)\s:(.*)))'
        formatted_text = re.split(expression, text)

        #return nothing if unable to find match
        if len(formatted_text) == 1:
            content['channel'],content['type'] = (None,None)
            return content

        #Begin checking each case

        #NICK
        if formatted_text[16] == 'NICK':
            content['type'] = 'NICK'
            content['channel'] = None
            content['name'] = formatted_text[1] #old nick
            content['message'] = formatted_text[17]#new nick
            return content

        #KICK
        elif formatted_text[19] == 'KICK':
            content['type'] = 'KICK'
            content['channel'] = formatted_text[20]
            content['name'] = formatted_text[21]
            content['message'] = 'was kicked by %s' %(formatted_text[1])
            if content['name'] == self.botnick:
                #:SoraSky!~sora@always.online-never.available KICK #nanodesu kick_me_pls :test
                text = 'JOIN '+content['channel']+'\n'
                self.irc.send(text.encode())
            return content

        #JOIN
        elif formatted_text[23] == 'JOIN':
            content['type'] = 'JOIN'
            content['channel'] = formatted_text[24]
            content['name'] = formatted_text[1]
            content['message'] = ''
            return content

        #PART
        elif formatted_text[13] == 'PART':
            content['type'] = 'PART'
            content['channel'] = formatted_text[14]
            content['name'] = formatted_text[1]
            content['message'] = ''
            return content

        #QUIT
        elif formatted_text[11] == 'QUIT':
            content['type'] = 'QUIT'
            content['message'] = ''
            content['name'] = formatted_text[1]
            content['channel'] = self.channel #It doesn't matter
            return content

        #PRIVMSG
        elif formatted_text[7] == 'PRIVMSG':
            content['type'] = 'PRIVMSG'
            content['message'] = formatted_text[9]
            content['name'] = formatted_text[1]
            content['channel'] = formatted_text[8]
            if not content['channel'].startswith('#'):
                content['private_messaged'] = True
            return content

        #NAMELIST
        elif formatted_text[26] == '353':
            content['private_messaged'] = True
            content['type'] = 'NAMELIST'
            content['channel'] = formatted_text[27]
            content['message'] = formatted_text[28]
            content['name'] = ''
            return content
