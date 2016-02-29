import threading
import socket
import sys
import queue

class IRC(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = "irc.rizon.net"       #settings
        self.channel = "#nanodesu"
        self.botnick = "Muse-chan-clone"
        self.inputs = queue.Queue()
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, 6667))
        self.connect()
    def connect(self):
        a = "USER "+ self.botnick +" "+ self.botnick +" "+ self.botnick +" :Muse-chan\n"
        b = "NICK "+ self.botnick +"\n"
        c = "PRIVMSG nickserv :lalala\r\n"
        d = "JOIN "+ self.channel +"\n"
        
        self.irc.send(a.encode())   #user authentication
        self.irc.send(b.encode())   #sets nick
        self.irc.send(c.encode())    #auth
        self.irc.send(d.encode())   #join the chan
    def run(self):
        while 1:    #puts it in a loop
            try:
                text=self.irc.recv(2040).decode()  #receive the text
            except:
                pass
            print (text)   #print text to console
            pong = 'PONG ' + text.split()[1] + '\r\n'
            if text.find('PING :') != -1:   #check if 'PING' is found
                self.irc.send(pong.encode())    #returns 'PONG' back to the server (prevents pinging out!)
            elif not self.formatter(text)['type'] == None:   #Only registering recognized events. (JOIN, PRIVMSG)
                self.inputs.put(self.formatter(text))
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
            dict['message'] = text[2].rstrip('\r\n')
            dict['name'] = text[1].split('!')[0]
        except:
            pass
        dict['private_messaged'] = False
        if 'PRIVMSG' in text[1]:
            dict['type'] = 'PRIVMSG'
            dict['channel'] = text[1].split('PRIVMSG ',1)[1].split(' ',1)[0]
            if dict['channel'] == self.botnick:
                dict['private_messaged'] = True
        elif 'JOIN' in text[1]:
            dict['type'] = 'JOIN'   #when a person joins a channel, the channel is reflected in text[2], after the ':', hence get channel from dict['message']
            dict['channel'] = text[2]
            dict['message'] = ''
        else:
            dict['channel'], dict['type'] = (None,None)
        return dict
