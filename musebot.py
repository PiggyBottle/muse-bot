import datetime
import time
import pickle
import threading
import hexchat
__module_name__ = "Hexchat Muse"
__module_version__ = "1.0"
__module_description__ = "Implemented state machine."
__author__ = "Sora & Yarn & Valdars"

#ideas: poll that has multiple answers, daily poll
#to-implement: difflib.sequencematcher, closures, regex

datapicklelocation = '/home/yj/Documents/data.pickle'


def day_counter(date):
    counter = 0
    start_counting = False
    current_weekday = datetime.date.today().isoweekday()
    if current_weekday == date:
        return 0
    for a in [1,2,3,4,5,6,7,1,2,3,4,5,6]:
        if start_counting == False and a == current_weekday:
            start_counting = True
        elif start_counting == True and a != date:
            counter += 1
        elif start_counting == True and a == date:
            counter +=1
            break
    return counter

class main():
    def __init__(self):
        hexchat.hook_print("Channel Message",self.menu)
    def menu(self, word, word_eol, userdata):
        #added a space after @test to make sure @testt doesnt work
        if '@test ' == word[1][0:6]:
            
            return hexchat.EAT_ALL
        elif word[1].startswith('$anime '):
            f = open(datapicklelocation,'rb')
            anime_showtime = pickle.load(f)['anime_showtime']
            f.close()
            for a in anime_showtime.keys():
                if a in word[1].lower():
                    days = day_counter(anime_showtime[a][0])
                    hours = anime_showtime[a][1] - datetime.datetime.today().hour
                    minutes = anime_showtime[a][2] - datetime.datetime.today().minute
                    if minutes < 0:
                        minutes = 60 + minutes
                        hours -= 1
                    if hours < 0:
                        hours = 24 + hours
                        if days == 0:
                            days = 6
                        else:
                            days -= 1
                    if days == 6:
                        hexchat.command('say '+anime_showtime[a][3]+' subs has just recently been released. Check it out now!')
                    else:
                        hexchat.command('say '+anime_showtime[a][3]+' subs will be released in %d days, %d hours and %d minutes.' %(days,hours,minutes))
                    break
            return hexchat.EAT_ALL

        elif word[1].startswith('$poll '):
            self.manager.transition(poll(word, word_eol, userdata))
            
        elif word[1][0:13] == '$settimezone ':
            hexchat.prnt(word[1][13:])
            try:
                timezone = int(word[1][13:])
            except:
                hexchat.command('say That is not a number!')
                return hexchat.EAT_ALL
            if not (timezone >= -12) and (timezone <= 14):
                hexchat.command('say Error: Invalid time zone.')
                return hexchat.EAT_ALL
            f = open(datapicklelocation,'rb')
            data = pickle.load(f)
            f.close()
            name = str(word[0]).lower()
            data['usertimezones'][name] = timezone
            f = open(datapicklelocation,'wb')
            pickle.dump(data,f)
            f.close()
            hexchat.command('say Timezone set to '+str(timezone)+', remember to update this when DST starts/ends!')
            return hexchat.EAT_ALL

        elif word[1].startswith('$time '):
            f = open(datapicklelocation,'rb')
            data = pickle.load(f)
            f.close()
            found = False
            if len(word[1][6:]) == 0:
                hexchat.command('say Error: Please enter a user\'s name.')
                return hexchat.EAT_ALL
            for a in data['usertimezones'].keys():
                if word[1][6:].lower().replace(' ','') in a:
                    found = True
                    timezone = data['usertimezones'][a]
                    time = datetime.datetime.utcnow() + datetime.timedelta(hours=timezone)
                    if time.hour < 10:
                        hour_zero = str(0)
                    else:
                        hour_zero = ''
                    if time.minute < 10:
                        minute_zero = str(0)
                    else:
                        minute_zero = ''
                    hexchat.command('say It is currently '+hour_zero+str(time.hour)+':'+minute_zero+str(time.minute)+' in '+str(a)+'\'s country.')
                    break
            if found == False:
                hexchat.command('say Either this person has not registered, or such person does not exist.')
            
            return hexchat.EAT_ALL
            
       # elif word[0].lower().startswith('nano') and word[1] == 'lol':
            #hexchat.command('say .quote read 468')

        else:
            f = open(datapicklelocation,'rb')
            data = pickle.load(f)
            f.close()
            data['active_users'][word[0]] = datetime.time()
            f = open(datapicklelocation,'wb')
            pickle.dump(data,f)
            f.close()
            return hexchat.EAT_ALL

class poll():
    def __init__(self, word, word_eol, userdata):
        self.score = {'y':0, 'n':0}
        self.voters = []
        hexchat.hook_print("Channel Message",self.menu)
        hexchat.command('say Poll has started!')
        hexchat.command('say Topic: \"'+word[1][6:]+'\" ')
        hexchat.command('say Type y or n to vote!')
        t = threading.Timer(15, self.complete)
        t.start()
    def menu(self, word, word_eol, userdata):
        if (word[1].lower() == 'y' or word[1].lower() == 'n') and not word[0] in self.voters:
            self.voters.append(word[0])
            self.score[word[1].lower()] += 1
        return hexchat.EAT_ALL
    def complete(self):
        hexchat.command('say done!')
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
            hexchat.command('say The majority has spoken: '+self.answer)
        elif self.answer == 'zero':
            hexchat.command('say Apparently nobody cares about this.')
        else:
            hexchat.command('say We have a tie!')
        hexchat.prnt('say '+str(self.score))
        self.manager.transition(main())
        
class state_manager():
    def __init__(self):
        self.transition(main())
    def transition(self, new):
        self.state = new
        self.state.manager = self

state = state_manager()
#remember that every new state class has to initialize with a hexchat.hook_print("Channel Message",self.menu)

hexchat.prnt('loaded')
