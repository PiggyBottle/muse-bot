



class Poll():
    def __init__(self, irc):
        self.irc = irc
        self.score = {'y':0, 'n':0}
        self.voters = []
        self.started = False
    def execute(self, content):
        if self.started == False:
            self.started = True
            self.channel = content['channel']  #to ensure that only voters in the same channel count
            return str('Poll has started!\r\n%s %s :Topic: \"%s\"\r\n%s %s :Type y/n to vote!' %(content['type'], dict['channel'], dict['message'][6:], dict['type'], dict['channel']))    #every new line out needs to have 'PRIVMSG #channel name :text'
        if (content['message'].lower() == 'y' or dict['message'].lower() == 'n') and dict['channel'] == self.channel and not dict['name'] in self.voters:
            self.voters.append(content['name'])
            self.score[content['message'].lower()] += 1
        return
    def complete(self, content, sm):
        sm.state = 'main'
        output = ''
        #if less than 3 ppl voted, no one cares. otherwise, show result of yes, no or tie
        if len(self.voters) < 3:
            self.answer = 'zero'
        elif self.score['y'] > self.score['n']:
            self.answer = 'YES!'
        elif self.score['y'] < self.score['n']:
            self.answer = 'NO!'
        else:
            self.answer = 'draw'
        if self.answer == 'YES!' or self.answer == 'NO!':
            output += 'The majority has spoken: '+self.answer + '\r\n' + content['type'] + ' ' + dict['channel'] + ' :'
        elif self.answer == 'zero':
             output += 'Apparently nobody cares about this.' + '\r\n' + content['type'] + ' ' + dict['channel'] + ' :'
        else:
            output += 'We have a tie!' + '\r\n' + content['type'] + ' ' + dict['channel'] + ' :'
        output += ''+str(self.score['y'])+' vote(s) for \'Yes\' and '+str(self.score['n'])+' vote(s) for \'No\'!'
        content['message'] = output
        self.irc.send(content)
