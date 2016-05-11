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



class StateManager():
    def __init__(self, config, irc, dpl, lpl, tpl, annpl):
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
        self.trackers = trackers.Trackers(self.irc,self.tpl,self.annpl,self.config['master'],animetiming.AnimeTiming(self.dpl))
        self.trackers.start()
        self.logger = logger.Logger(self.dpl, self.lpl)
        self.spamguard = spamguard.SpamGuard()
        self.tell = tell.Tell()
        self.emailer = emailer.Emailer(config)
    def main(self, dict):

        #Checking Spamguard permissions
        dict, permissions = self.spamguard.check(dict,self.state)
        if 'SpamGuard: ' in dict['message']:
            return dict
        if not permissions == 'block' and not permissions == 'do not log':
            self.logger.log(dict,self.trackers.namelist)
        if not (permissions == 'open' or permissions == 'do not log'):
            return

        #Updating trackers namelist
        if dict['type'] in ['NAMELIST', 'PART', 'KICK', 'QUIT', 'JOIN', 'NICK']:
            self.trackers.update_namelist(dict)

        message = dict['message']
        '''
        if (message.startswith('!tell ') or message.startswith('$tell')) and len(message) > 6:
            return self.tell.write(dict)
        if dict['type'] == 'PRIVMSG':
            tells, buffer = self.tell.check(dict)
            if tells:
                return buffer
        '''
        if message.startswith('$anime ') and len(message) > 7 and self.commands['anime'] == True:
            a = animetiming.AnimeTiming(self.dpl)
            dict['message'] = a.execute(message[7:])
            return dict
        elif self.commands['time'] == True and (message.startswith('$time') or message.startswith('$settimezone ')):
            a = usertimes.TimeZoneCheck()
            dict['message'] = a.execute(dict, self.dpl)
            return dict
        elif self.commands['poll'] == True and dict['private_messaged'] == False and message.startswith('$poll ') and len(message) > 6 and self.state != 'poll':
            self.state = 'poll'
            self.function = poll.Poll(self.irc)
            dict['message'] = self.function.execute(dict)
            #plus start thread over here
            t = threading.Timer(15,self.function.complete, [dict, self])
            t.start()
            return dict
        elif self.state == 'poll':
            return self.function.execute(dict)
        elif self.commands['money'] == True and message.startswith('$money'):
            a = money.Money(self.dpl)
            return a.report(dict)
        elif self.commands['blackjack'] == True and message.startswith('$blackjack') and self.state != 'blackjack':
            a = money.Money(self.dpl)
            #To make sure a person who is broke cannot start a game of blackjack
            if a.check(dict['name']) == 0:
                dict['message'] = 'Error, player has no money!'
                return dict
            self.state = 'blackjack'
            self.commands['poll'],self.commands['loan'] = False,False
            self.function = blackjack.Game(dict, self.dpl)
            return self.function.execute(dict)
        elif self.state == 'blackjack':
            if (message.startswith('$quit') and dict['name'].lower() in self.function.lower_keys()) or len(self.function.lower_keys()) < 1:
                self.function = None
                self.commands['poll'],self.commands['loan'] = True,True
                self.state = 'main'
                dict['message'] = 'Game closed.'
                return dict
            elif dict['type'] == 'NICK' and dict['name'].lower() in self.function.lower_keys():
                self.commands['poll'],self.commands['loan'] = True,True
                self.state = 'main'
                dict['message'] = 'A nick change has been detected. Game closing.'
                dict['type'] = 'PRIVMSG'
                dict['channel'] = self.function.channel
                self.function = None
                return dict
            return self.function.execute(dict)
        elif self.commands['loan'] == True and not self.state == 'loan' and message.startswith('$loan'):
            self.function = money.Money(self.dpl)
            dict,move_on = self.function.loan(dict)
            if move_on == False:
                self.function = None
            elif move_on == True:
                self.state = 'loan'
                self.commands['blackjack'],self.commands['loan'] = False,False
            return dict
        elif self.state == 'loan':
            dict,finish = self.function.loan(dict)
            if finish:
                self.function = None
                self.commands['blackjack'],self.commands['loan'] = True,True
                self.state = 'main'
            return dict
        elif message.startswith('$debt'):
            a = money.Money(self.dpl)
            debt = a.check_debt(dict['name'])
            if debt == 0:
                dict['message'] = 'You have no $debt!'
            else:
                dict['message'] = 'You have %d NanoDollars of debt.' %(debt)
            return dict
        elif message.startswith('$pay') and self.state == 'main':
            #forcing state to be 'main' to prevent people from paying money in the middle of a blackjack game
            a = money.Money(self.dpl)
            return a.pay_debt(dict)
        elif message.startswith('$help') and self.state == 'main':
            a = helper.Helper()
            dict = a.execute(dict)
            return dict
        elif message.startswith('$log'):
            dict = self.logger.read(dict)
            return dict
        elif message.startswith('\x01ACTION looks at %s' %(self.irc.botnick)):
            dict['message'] = '\x01ACTION looks at %s' %(dict['name'])
            return dict
        elif message.startswith ('$NDAemail '):
            #Emails sent represent NanoDesu Translations. Don't misuse this.
            self.emailer.send([message.split()[1]],[],['viorama@gmail.com'],'Confirmation of receipt of your ND Academy application',self.emailer.get_template('emails/NDAtemplate.txt'))
            dict['message'] = 'Email sent!'
            return dict

