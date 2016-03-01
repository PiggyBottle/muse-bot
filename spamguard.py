import time



class SpamGuard():
    def __init__(self):
        self.blocking = False
        self.restricted = ['jonathanasdf','jsdf']
        self.blocklist = ['Trivia', 'Internets','Icara','Tokino', 'Quotes']
        self.readlog_time = 0

    def check(self, dict):
        if dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and dict['message'].startswith('Starting round'):
            self.blocking = True
            dict['message'] = 'SpamGuard: Trivia detected. All commands and logging are now blocked.'
            return dict, 'block'
        elif dict['type'] == 'PRIVMSG' and dict['name'] == 'Trivia' and (dict['message'].startswith('Round of ') or dict['message'].startswith('Trivia stopped')):
            dict['message'] = 'SpamGuard: Trivia has ended. Commands and logging are now enabled.'
            self.blocking = False
            return dict, 'block'
        elif self.blocking == False and dict['name'] in self.restricted:
            return dict, 'log'
        elif self.blocking == False and dict['message'].startswith('$log'):
            if time.time() - self.readlog_time < 10:
                dict['message'] = 'SpamGuard: $log command blocked for 10 secs.'
                return dict, 'open'
            else:
                self.readlog_time = time.time()
                return dict, 'open'
        elif self.blocking == True or dict['name'] in self.blocklist:
            return dict, 'block'
        elif self.blocking == False:
            return dict, 'open'
        
