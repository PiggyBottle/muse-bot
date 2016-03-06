import time



class SpamGuard():
    def __init__(self):
        self.blocking = False
        self.restricted = ['jonathanasdf','jsdf']
        self.blocklist = ['Trivia', 'Internets','Icara','Tokino', 'Quotes']
        self.readlog_time = 0
        self.commandlist = '$money $time $anime $blackjack $log .trivia .strivia .quote !snowball !ne~ !love !seen .cc !hangman !5050'.split()

    def check(self, dict, state):
        if dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and dict['message'].startswith('Starting round'):
            self.blocking = True
            dict['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return dict, 'block'
        elif self.blocking == True and dict['type'] == 'PRIVMSG' and ((dict['name'] == 'Trivia' and dict['message'].startswith('Round of ') or dict['message'].startswith('Trivia stopped')) or dict['message'].startswith('.strivia')):
            dict['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            self.blocking = False
            return dict, 'block'
        elif dict['type'] == 'PRIVMSG' and dict['message'].startswith('!hangman'):
            dict['message'] = 'SpamGuard: Hangman detected. All commands and logging are now blocked.'
            self.blocking = True
            return dict, 'block'
        elif self.blocking == True and dict['type'] == 'PRIVMSG' and (dict['message'].startswith('FAILURE! ') or dict['message'].startswith('Correct! ')):
            self.blocking = False
            dict['message'] = 'SpamGuard: Hangman has ended. Commands and logging are now enabled'
            return dict, 'block'

        elif self.blocking == False and dict['name'] in self.restricted:
            return dict, 'log'
        elif self.blocking == False and dict['message'].startswith('$log'):
            if time.time() - self.readlog_time < 10:
                dict['message'] = 'SpamGuard: $log command blocked for 10 secs.'
                return dict, 'do not log'
            else:
                self.readlog_time = time.time()
                return dict, 'do not log'
        elif self.blocking == True or dict['name'] in self.blocklist:
            return dict, 'block'
        elif self.blocking == False:
            found = False
            for a in self.commandlist:
                if a in dict['message']:
                    found = True
                    break
            if found == True:
                return dict, 'do not log'
            elif state == 'blackjack':
                return dict, 'do not log'
            else:
                return dict, 'open'
        
