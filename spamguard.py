



class SpamGuard():
    def __init__(self):
        self.blocking = False
        self.blocklist = ['jonathanasdf','jsdf']
        self.restricted = []

    def check(self, dict):
        if dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and dict['message'].startswith('Starting round'):
            self.blocking = True
            dict['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return dict, 'block'
        elif dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and (dict['message'].startswith('Round of ') or dict['message'].startswith('Trivia stopped')):
            dict['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            self.blocking = False
            return dict, 'block'
        elif self.blocking == True:
            return dict, 'block'
        elif self.blocking == False and dict['name'] in self.blocklist:
            return dict, 'log'
        elif self.blocking == False:
            return dict, 'open'
