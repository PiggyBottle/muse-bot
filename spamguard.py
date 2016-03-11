import time



class SpamGuard():
    def __init__(self):
        self.blocking = False
        self.restricted = ['jonathanasdf','jsdf','dmitri']
        self.blocklist = ['Trivia', 'Internets','Icara','Tokino', 'Quotes']
        self.readlog_time = 0
        self.commandlist = '$money $time $anime $blackjack $loan $pay $debt $log .trivia .strivia .quote !snowball !ne~ !love !seen .cc !hangman !5050 .rank .t !rr !pull !roulette'.split()
        self.states = {}    #using a dict to make it easier to delete keys

    def manage_states(self, state):
        if state == 'blackjack' and not state in self.states.keys():
            self.states['blackjack'] = True
        elif state != 'blackjack' and 'blackjack' in self.states.keys():
            del self.states['blackjack']
        if len(self.states.keys()) == 0 or (len(self.states.keys()) == 1 and 'blackjack' in self.states.keys()):
            self.blocking = False
        else:
            self.blocking = True
            
    def check(self, dict, state):
        self.manage_states(state)
        ###start trivia###
        if dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and dict['message'].startswith('Starting round'):
            ###interrupt trivia###
            if len(self.states.keys()) > 0:
                dict['message'] = '.strivia\r\n%s %s :SpamGuard: Do not spam the chat!' %(dict['type'], dict['channel'])
            else:
                self.states['trivia'] = True
                dict['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return dict, 'block'
        ###interrupt blackjack###
        elif dict['type'] == 'PRIVMSG' and dict['message'].startswith('$blackjack') and not 'blackjack' in self.states.keys() and len(self.states.keys()) > 0:
            dict['message'] = 'SpamGuard: Terminate all other functions before starting $blackjack.'
            return dict, 'block'
        ###interrupt hangman###
        elif dict['type'] == 'PRIVMSG' and dict['message'].startswith('!hangman') and len(self.states.keys()) > 0 and not 'hangman' in self.states.keys():
            dict['message'] = 'SpamGuard: Do not spam!\r\nKICK %s %s :' %(dict['channel'], dict['name'])
            return dict, 'block'
        ###start hangman###
        elif dict['type'] == 'PRIVMSG' and (dict['name'].lower() == 'tokino' or dict['name'].lower() == 'icara') and ' has began a game of hangman!' in dict['message']:
            dict['message'] = 'SpamGuard: Hangman detected. All commands and logging are now blocked.'
            self.states['hangman'] = True
            return dict, 'block'
        ###end trivia###
        elif 'trivia' in self.states.keys() and dict['type'] == 'PRIVMSG' and ((dict['name'] == 'Trivia' and dict['message'].startswith('Round of ') or dict['message'].startswith('Trivia stopped')) or dict['message'].startswith('.strivia')):
            if len(self.states.keys()) == 1:
                dict['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            del self.states['trivia']
            return dict, 'block'
        ###end hangman###
        elif 'hangman' in self.states.keys() and dict['type'] == 'PRIVMSG' and (dict['message'].startswith('FAILURE! ') or dict['message'].startswith('Correct! ')):
            if len(self.states.keys()) == 1:
                dict['message'] = 'SpamGuard: Hangman has ended. Commands and logging are now enabled'
            del self.states['hangman']
            return dict, 'block'
        ###instant blocks###
        elif self.blocking == True or dict['name'] in self.blocklist:
            return dict, 'block'
        elif self.blocking == False:
            ###restricted###
            if dict['name'].lower() in self.restricted:
                return dict, 'log'
            ###throttle logs###
            elif dict['message'].startswith('$log'):
                if time.time() - self.readlog_time < 10:
                    dict['message'] = 'SpamGuard: $log command blocked for 10 secs.'
                    return dict, 'do not log'
                else:
                    self.readlog_time = time.time()
                    return dict, 'do not log'
            else:
                found = False
                for a in self.commandlist:
                    if dict['message'].startswith(a):
                        found = True
                        break
                if found == True:
                    return dict, 'do not log'
                elif 'blackjack' in self.states.keys():
                    return dict, 'do not log'
                else:
                    return dict, 'open'

'''
##################################################
        if dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and dict['message'].startswith('Starting round'):
            self.blocking = True
            self.states['trivia'] = True
            dict['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return dict, 'block'
        elif self.blocking == True and dict['type'] == 'PRIVMSG' and ((dict['name'] == 'Trivia' and dict['message'].startswith('Round of ') or dict['message'].startswith('Trivia stopped')) or dict['message'].startswith('.strivia')):
            dict['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            self.blocking = False
            del self.states['trivia']
            return dict, 'block'
        elif dict['type'] == 'PRIVMSG' and (dict['name'].lower() == 'tokino' or dict['name'].lower() == 'icara') and ' has began a game of hangman!' in dict['message']:
            dict['message'] = 'SpamGuard: Hangman detected. All commands and logging are now blocked.'
            self.blocking = True
            self.states['hangman'] = True
            return dict, 'block'
        elif self.blocking == True and dict['type'] == 'PRIVMSG' and (dict['message'].startswith('FAILURE! ') or dict['message'].startswith('Correct! ')):
            self.blocking = False
            del self.states['hangman']
            dict['message'] = 'SpamGuard: Hangman has ended. Commands and logging are now enabled'
            return dict, 'block'

        elif self.blocking == False and dict['name'].lower() in self.restricted:
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
                if dict['message'].startswith(a):
                    found = True
                    break
            if found == True:
                return dict, 'do not log'
            elif state == 'blackjack':
                return dict, 'do not log'
            else:
                return dict, 'open'
'''
