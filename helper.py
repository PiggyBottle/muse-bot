class Helper():
    def __init__(self):
        self.list = 'poll, anime, [time, settimezone], blackjack, [money, loan, debt, pay], log, s/'
    def execute(self, content):
        if len(content['message']) <= 6:
            if content['private_messaged'] == False:
                content['message'] = 'Type $help <command> for details.\r\n%s %s :%s.' %(content['type'],content['channel'],self.list)
            elif content['private_messaged'] == True:
                content['message'] = 'Type $help <command> for details.\r\n%s %s :%s.' %(content['type'],content['name'],self.list)
            return content
        elif len(content['message']) > 6:
            option = content['message'][6:]
            if option.startswith('poll'):
                content['message'] = '$poll <question> starts a poll with <question>.'
            elif option.startswith('anime'):
                content['message'] = '$anime <title> gives the time left until the next subbed episode of <title> is released. Some short forms of <title> are accepted.'
            elif option.startswith('time'):
                content['message'] = '$time <person> displays the current time in <person>\'s time zone. Leaving <person> blank gives user\'s own time. Only works when time zone is set.'
            elif option.startswith('settimezone'):
                content['message'] = '$settimezone <number> sets your time zone to UTC +/- <number>.'
            elif option.startswith('blackjack'):
                content['message'] = '$blackjack starts a game of blackjack. Minimum of 1 NanoDollar required.'
            elif option.startswith('money'):
                content['message'] = '$money displays the amount of NanoDollars you have under your nick. (Everyone starts with 10.)'
            elif option.startswith('loan'):
                content['message'] = 'When you are in need of money, use $loan <number> to request for one. Note that you cannot use $loan when in $debt, and having one can limit your rights.'
            elif option.startswith('debt'):
                content['message'] = '$debt displays the amount of money you currently owe. Having a $debt severely limits your rights.'
            elif option.startswith('pay'):
                content['message'] = '$pay <number> pays off <number> from your debt. Note that you do not need to repay your debt in full.'
            elif option.startswith('log'):
                content['message'] = '$log generates a log of messages you\'ve missed since you last left the channel. Requires a time zone to be set.'
            elif option.startswith('s/'):
                content['message'] = 's/ is a regular expression substitution function. The syntax for use is `s/<Expression to be replaced>/<Replacement string>/<Modifier Flag>`. ' + \
                                     'The flags available are i (case insensitivity) and g (global). For futher understanding of regular expressions, I recommend http://regexr.com .'
            else:
                content['message'] = 'Type $help <command> for details.\r\n%s %s :%s.' %(content['type'],content['channel'],self.list)
            return content
