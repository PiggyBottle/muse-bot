import datetime
import time
import pickle
import threading
import hexchat
__module_name__ = "Hexchat Muse"
__module_version__ = "1.0"
__module_description__ = "Implemented state machine."
__author__ = "Sora & Yarn & Valdars"

datapicklelocation = 'D:\Documents\muse-bot\data.pickle'


class StateManager():
    def __init__(self):
        hexchat.prnt('loaded')
        hexchat.hook_print('Channel Message', self.main)
        self.state = 'main_menu'
    def main(self, word, word_eol, userdata):
        if self.state == 'main_menu':
            self.main_menu(word, word_eol, userdata)
        if self.state == 'poll':
            self.poll(word, word_eol, userdata)
    def main_menu(self, word, word_eol, userdata):
        if '@test ' == word[1][0:6]:
            hexchat.prnt('Success')
            return hexchat.EAT_ALL
        elif word[1].startswith('$anime '):
            self.function = AnimeTiming(word[1][7:])
            self.function = None
            return hexchat.EAT_ALL
        elif word[1].startswith('$poll '):
            self.state = 'poll'
            self.function = Poll(word[1][6:])
            self.t = threading.Timer(15, self.poll_complete)
            self.t.start()
            return hexchat.EAT_ALL
        elif word[1][0:13] == '$settimezone ' or word[1].startswith('$time'):
            self.function = TimeZoneCheck(word[1], word[0].lower())
            self.function = None
            return hexchat.EAT_ALL
        else:
            self.setactiveuser(word[0])
            return hexchat.EAT_ALL

    def setactiveuser(self,w):       
        f = open(datapicklelocation,'rb')
        data = pickle.load(f)
        f.close()
        data['active_users'][w] = time.time()
        f = open(datapicklelocation,'wb')
        pickle.dump(data,f)
        f.close()
    def poll(self, word, word_eol, userdata):
        self.function.main(word, word_eol, userdata)
    def poll_complete(self):
        self.function.complete()
        self.state = 'main_menu'
        self.function = None
        
class AnimeTiming():
    def __init__(self, w):
        self.word = w
        self.time_left(self.word)
        try:
            self.days, self.hours, self.minutes, self.title = self.time_left(self.word)
            if self.days == 6:
                hexchat.command('say '+self.title+' subs has just recently been released. Check it out now!')
            else:
                hexchat.command('say %s subs will be released in %d days, %d hours and %d minutes.' %(self.title, self.days,self.hours,self.minutes))
        except:
            hexchat.command('say Error: Anime not found')
        
    def day_counter(self,date):
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
    def time_left(self,w):
        f = open(datapicklelocation,'rb')
        anime_showtime = pickle.load(f)['anime_showtime']
        f.close()
        for a in anime_showtime.keys():
            if w.lower() in a:
                days =self.day_counter(anime_showtime[a][0])
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
                return days, hours, minutes, anime_showtime[a][3]


class Poll():
    def __init__(self, w):
        hexchat.command('say Poll has started!')
        hexchat.command('say Topic: \"'+w+'\" ')
        hexchat.command('say Type y or n to vote!')
        self.score = {'y':0, 'n':0}
        self.voters = []
    def main(self, word, word_eol, userdata):
        if (word[1].lower() == 'y' or word[1].lower() == 'n') and not word[0] in self.voters:
            self.voters.append(word[0])
            self.score[word[1].lower()] += 1
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
            
class TimeZoneCheck():
    def __init__(self, word, name):
        self.word = word
        self.name = name
        if self.word.startswith('$settimezone '):
            self.set_time(self.name, self.word[13:])
        elif self.word.startswith('$time '):
            self.read_time(self.word[6:])
        elif self.word == '$time':
            self.read_time(self.name)
        
    def set_time(self, name, tz):
        try:
            timezone = int(tz)
        except:
            hexchat.command('say That is not a number!')
            return hexchat.EAT_ALL
        if not ((timezone >= -12) and (timezone <= 14)):
            hexchat.command('say Error: Invalid time zone.')
            return hexchat.EAT_ALL
        f = open(datapicklelocation,'rb')
        data = pickle.load(f)
        f.close()
        data['usertimezones'][name] = timezone
        f = open(datapicklelocation,'wb')
        pickle.dump(data,f)
        f.close()
        hexchat.command('say Timezone set to '+str(timezone)+', remember to update this when DST starts/ends!')
        return hexchat.EAT_ALL

    def read_time(self, name):
        f = open(datapicklelocation,'rb')
        data = pickle.load(f)
        f.close()
        found = False
        if len(name) == 0:
            hexchat.command('say Error: Please enter a user\'s name.')
            return hexchat.EAT_ALL
        for a in data['usertimezones'].keys():
            if name.lower().replace(' ','') in a:
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
                hexchat.command('say It is currently '+hour_zero+str(time.hour)+':'+minute_zero+str(time.minute)+' in '+str(a)+'\'s time zone.')
                break
        if found == False:
            hexchat.command('say Either this person has not registered, or such person does not exist.')
        return hexchat.EAT_ALL



bot = StateManager()

