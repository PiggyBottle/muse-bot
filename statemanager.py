import animetiming
import usertimes
import threading
import poll
import money
import blackjack



class StateManager():
    def __init__(self, irc):
        self.irc = irc
        self.state = 'main'
        self.commands = {'time':True, 'money': True, 'poll':True, 'anime':True, 'blackjack':True}
        #remember to add self.dpl into functions that need pickle!
        self.dpl = 'D:\Documents\muse-bot\data.pickle'
    def main(self, dict):
        message = dict['message']
        if message.startswith('$anime ') and len(message) > 7 and self.commands['anime'] == True:
            a = animetiming.AnimeTiming()
            dict['message'] = a.execute(message[7:],self.dpl)
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
            self.commands['poll'] = False
            self.function = blackjack.Game(dict, self.dpl)
            return self.function.execute(dict)
        elif self.state == 'blackjack':
            if (message.startswith('$quit') and dict['name'].lower() in self.function.lower_keys()) or len(self.function.lower_keys()) < 1:
                self.function = None
                self.commands['poll'] = True
                self.state = 'main'
                dict['message'] = 'Game closed.'
                return dict
            return self.function.execute(dict)
        
