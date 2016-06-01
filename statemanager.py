import animetiming
import usertimes
import threading
import poll
import money
import blackjack
import logger
import spamguard
import helper
import trackers
import tell
import emailer
import regex
import ndacademy
import japanesehelper

class StateManager():
    def __init__(self, config, irc, dpl, lpl, tpl, annpl, ndapl):
        self.config = config
        self.irc = irc
        self.state = 'main'
        self.commands = {'time':True, 'money': True, 'poll':True, 'anime':True, 'blackjack':True, 'loan':True}
        #remember to add self.dpl into functions that need pickle!
        self.dpl = dpl
        self.lpl = lpl
        self.tpl = tpl
        self.annpl = annpl
        self.master = config['master']
        self.emailer = emailer.Emailer(config)
        self.nda = ndacademy.NDAcademy(self.emailer,ndapl, self.irc)
        self.trackers = trackers.Trackers(self.irc,self.tpl,self.annpl,self.config['master'],animetiming.AnimeTiming(self.dpl),self.nda)
        self.trackers.start()
        self.logger = logger.Logger(self.dpl, self.lpl)
        self.spamguard = spamguard.SpamGuard()
        self.tell = tell.Tell()
        self.regex = regex.Regex(self.logger)
        self.japanesehelper = japanesehelper.JapaneseHelper()

    def main(self, content):

        #Checking Spamguard permissions
        content, permissions = self.spamguard.check(content,self.state)
        if 'SpamGuard: ' in content['message']:
            return content
        if not permissions == 'block' and not permissions == 'do not log':
            self.logger.log(content,self.trackers.namelist)
        if not (permissions == 'open' or permissions == 'do not log'):
            return

        #Updating trackers namelist
        if content['type'] in ['NAMELIST', 'PART', 'KICK', 'QUIT', 'JOIN', 'NICK']:
            self.trackers.update_namelist(content)

        message = content['message']
        if self.config['tell'] == True:
            if (message.startswith('!tell ') or message.startswith('$tell')) and len(message) > 6:
                return self.tell.write(content)
            if content['type'] == 'PRIVMSG':
                tells, buffer = self.tell.check(content)
                if tells:
                    return buffer
        if message.startswith('$anime ') and len(message) > 7 and self.commands['anime'] == True:
            a = animetiming.AnimeTiming(self.dpl)
            content['message'] = a.execute(message[7:])
            return content
        elif self.commands['time'] == True and (message.startswith('$time') or message.startswith('$settimezone ')):
            a = usertimes.TimeZoneCheck()
            content['message'] = a.execute(content, self.dpl)
            return content
        elif self.commands['poll'] == True and content['private_messaged'] == False and message.startswith('$poll ') and len(message) > 6 and self.state != 'poll':
            self.state = 'poll'
            self.function = poll.Poll(self.irc)
            content['message'] = self.function.execute(content)
            #plus start thread over here
            t = threading.Timer(15,self.function.complete, [content, self])
            t.start()
            return content
        elif self.state == 'poll':
            return self.function.execute(content)
        elif self.commands['money'] == True and message.startswith('$money'):
            a = money.Money(self.dpl)
            return a.report(content)
        elif self.commands['blackjack'] == True and message.startswith('$blackjack') and self.state != 'blackjack':
            a = money.Money(self.dpl)
            #To make sure a person who is broke cannot start a game of blackjack
            if a.check(content['name']) == 0:
                content['message'] = 'Error, player has no money!'
                return content
            self.state = 'blackjack'
            self.commands['poll'],self.commands['loan'] = False,False
            self.function = blackjack.Game(content, self.dpl)
            return self.function.execute(content)
        elif self.state == 'blackjack':
            if (message.startswith('$quit') and content['name'].lower() in self.function.lower_keys()) or len(self.function.lower_keys()) < 1:
                self.function = None
                self.commands['poll'],self.commands['loan'] = True,True
                self.state = 'main'
                content['message'] = 'Game closed.'
                return content
            elif content['type'] == 'NICK' and content['name'].lower() in self.function.lower_keys():
                self.commands['poll'],self.commands['loan'] = True,True
                self.state = 'main'
                content['message'] = 'A nick change has been detected. Game closing.'
                content['type'] = 'PRIVMSG'
                content['channel'] = self.function.channel
                self.function = None
                return content
            return self.function.execute(content)
        elif self.commands['loan'] == True and not self.state == 'loan' and message.startswith('$loan'):
            self.function = money.Money(self.dpl)
            content,move_on = self.function.loan(content)
            if move_on == False:
                self.function = None
            elif move_on == True:
                self.state = 'loan'
                self.commands['blackjack'],self.commands['loan'] = False,False
            return content
        elif self.state == 'loan':
            content,finish = self.function.loan(content)
            if finish:
                self.function = None
                self.commands['blackjack'],self.commands['loan'] = True,True
                self.state = 'main'
            return content
        elif message.startswith('$debt'):
            a = money.Money(self.dpl)
            debt = a.check_debt(content['name'])
            if debt == 0:
                content['message'] = 'You have no $debt!'
            else:
                content['message'] = 'You have %d NanoDollars of debt.' %(debt)
            return content
        elif message.startswith('$pay') and self.state == 'main':
            #forcing state to be 'main' to prevent people from paying money in the middle of a blackjack game
            a = money.Money(self.dpl)
            return a.pay_debt(content)
        elif message.startswith('$help') and self.state == 'main':
            a = helper.Helper()
            content = a.execute(content)
            return content
        elif message.startswith('$log'):
            content = self.logger.read(content)
            return content
        elif message.startswith('\x01ACTION looks at %s' %(self.irc.botnick)):
            content['message'] = '\x01ACTION looks at %s\x01' %(content['name'])
            return content
        elif message.startswith ('$NDAemail ') and content['name'] == self.master:
            #Emails sent represent NanoDesu Translations. Don't misuse this.
            self.emailer.send([message.split()[1]],[],['viorama@gmail.com'],'Confirmation of receipt of your ND Academy application',self.emailer.get_template('emails/NDAtemplate.txt'))
            content['message'] = 'Email sent!'
            return content
        elif message.startswith ('s/'):
            return self.regex.replace(content)
        elif message.startswith('$tatoeba '):
            return self.japanesehelper.tatoeba(content)


        
