import time



class SpamGuard():
    def __init__(self):
        self.blocking = False
        self.restricted = ['jsdf','dmitri', 'hobogunner']#'jonathanasdf'
        self.blocklist = ['Trivia', 'Internets','Icara','Tokino', 'Quotes']
        self.readlog_time = 0
        self.commandlist = '$money $time $anime $blackjack $loan $pay $debt $log $help .trivia .strivia .quote !snowball !ne~ !love !seen .cc !hangman !5050 .rank .t !rr !pull !roulette s/'.split()
        self.states = {}    #using a dict to make it easier to delete keys

    def manage_states(self, state):
        if state == 'blackjack' and not state in self.states.keys():
            self.states['blackjack'] = True
        elif state == 'loan' and not state in self.states.keys():
            self.states['loan'] = True
        elif state != 'blackjack' and 'blackjack' in self.states.keys():
            del self.states['blackjack']
        elif state != 'loan' and 'loan' in self.states.keys():
            del self.states['loan']
        if len(self.states.keys()) == 0 or (len(self.states.keys()) == 1 and ('blackjack' in self.states.keys() or 'loan' in self.states.keys())):
            self.blocking = False
        else:
            self.blocking = True

    def check(self, content, state):
        self.manage_states(state)
        ###start trivia###
        if content['type'] == 'PRIVMSG' and content['name'] == 'Trivia' and content['message'].startswith('Starting round'):
            ###interrupt trivia###
            if len(self.states.keys()) > 0:
                content['message'] = '.strivia\r\n%s %s :SpamGuard: Do not spam the chat!' %(content['type'], content['channel'])
            else:
                self.states['trivia'] = True
                content['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return content, 'block'
        ###interrupt blackjack###
        elif content['type'] == 'PRIVMSG' and content['message'].startswith('$blackjack') and not 'blackjack' in self.states.keys() and len(self.states.keys()) > 0:
            content['message'] = 'SpamGuard: Terminate all other functions before starting $blackjack.'
            return content, 'block'
        elif content['message'] == 'PRIVMSG' and content['message'].startswith('$loan') and not 'loan' in self.states.keys() and len(self.states.keys()) > 0:
            content['message'] = 'SpamGuard: Terminate all other functions before requesting a $loan.'
            return content, 'block'
        ###interrupt hangman###
        elif content['type'] == 'PRIVMSG' and content['message'].startswith('!hangman') and len(self.states.keys()) > 0 and not 'hangman' in self.states.keys():
            content['message'] = 'SpamGuard: Do not spam!\r\nKICK %s %s :' %(content['channel'], content['name'])
            return content, 'block'
        ###start hangman###
        elif content['type'] == 'PRIVMSG' and (content['name'].lower() == 'tokino' or content['name'].lower() == 'icara') and ' has began a game of hangman!' in content['message']:
            content['message'] = 'SpamGuard: Hangman detected. All commands and logging are now blocked.'
            self.states['hangman'] = True
            return content, 'block'
        ###end trivia###
        elif 'trivia' in self.states.keys() and content['type'] == 'PRIVMSG' and ((content['name'] == 'Trivia' and content['message'].startswith('Round of ') or content['message'].startswith('Trivia stopped'))):
            if len(self.states.keys()) == 1:
                content['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            del self.states['trivia']
            return content, 'block'
        ###end hangman###
        elif 'hangman' in self.states.keys() and content['type'] == 'PRIVMSG' and (content['message'].startswith('FAILURE! ') or content['message'].startswith('Correct! ')):
            if len(self.states.keys()) == 1:
                content['message'] = 'SpamGuard: Hangman has ended. Commands and logging are now enabled'
            del self.states['hangman']
            return content, 'block'
        ###instant blocks###
        elif self.blocking == True or content['name'] in self.blocklist:
            return content, 'block'
        elif self.blocking == False:
            ###restricted###
            if content['name'].lower() in self.restricted:
                return content, 'log'
            ###throttle logs###
            elif content['message'].startswith('$log'):
                if time.time() - self.readlog_time < 10:
                    content['message'] = 'SpamGuard: $log command blocked for 10 secs.'
                    return content, 'do not log'
                else:
                    self.readlog_time = time.time()
                    return content, 'do not log'
            else:
                found = False
                for a in self.commandlist:
                    if content['message'].startswith(a):
                        found = True
                        break
                if found == True:
                    return content, 'do not log'
                elif 'blackjack' in self.states.keys():
                    return content, 'do not log'
                else:
                    return content, 'open'

'''
##################################################
        if content['type'] == 'PRIVMSG' and content['name'] == 'Trivia' and content['message'].startswith('Starting round'):
            self.blocking = True
            self.states['trivia'] = True
            content['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return content, 'block'
        elif self.blocking == True and content['type'] == 'PRIVMSG' and ((content['name'] == 'Trivia' and content['message'].startswith('Round of ') or content['message'].startswith('Trivia stopped')) or content['message'].startswith('.strivia')):
            content['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            self.blocking = False
            del self.states['trivia']
            return content, 'block'
        elif content['type'] == 'PRIVMSG' and (content['name'].lower() == 'tokino' or content['name'].lower() == 'icara') and ' has began a game of hangman!' in content['message']:
            content['message'] = 'SpamGuard: Hangman detected. All commands and logging are now blocked.'
            self.blocking = True
            self.states['hangman'] = True
            return content, 'block'
        elif self.blocking == True and content['type'] == 'PRIVMSG' and (content['message'].startswith('FAILURE! ') or content['message'].startswith('Correct! ')):
            self.blocking = False
            del self.states['hangman']
            content['message'] = 'SpamGuard: Hangman has ended. Commands and logging are now enabled'
            return content, 'block'

        elif self.blocking == False and content['name'].lower() in self.restricted:
            return content, 'log'
        elif self.blocking == False and content['message'].startswith('$log'):
            if time.time() - self.readlog_time < 10:
                content['message'] = 'SpamGuard: $log command blocked for 10 secs.'
                return content, 'do not log'
            else:
                self.readlog_time = time.time()
                return content, 'do not log'
        elif self.blocking == True or content['name'] in self.blocklist:
            return content, 'block'
        elif self.blocking == False:
            found = False
            for a in self.commandlist:
                if content['message'].startswith(a):
                    found = True
                    break
            if found == True:
                return content, 'do not log'
            elif state == 'blackjack':
                return content, 'do not log'
            else:
                return content, 'open'
'''
