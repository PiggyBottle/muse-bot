import datetime
import time
import pickle

days = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]

class TimeZoneCheck():
    def __init__(self):
        pass
    def execute(self, dict, dpl):
        self.dict = dict
        self.word = self.dict['message']
        self.name = self.dict['name']
        self.dpl = dpl
        if self.word.startswith('$settimezone '):
            return self.set_time(self.name, self.word[13:])
        elif self.word.startswith('$time '):
            return self.read_time(self.word[6:])
        elif self.word == '$time':
            return self.read_time(self.name)

    def set_time(self, name, tz):
        if tz not in ['-12','-11','-10','-9.5','-9','-8.5','-8','-7','-6','-5','-5','-4','-3.5','-3','-2','-1','0','1','2','3','3','4','4.5','5','5.5','5.75','6','6.5','7','8','8.5','8.75','9','9.5','10','10.5','11','12','12.75','13','14']:
            return 'Invalid Time Zone'
        try:
            timezone = float(tz)
        except:
            return 'Error, that is not a number!'
        if not ((timezone >= -12) and (timezone <= 14)):
            return 'Error: Invalid time zone.'
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        data['usertimezones'][name.lower()] = timezone
        f = open(self.dpl,'wb')
        pickle.dump(data,f)
        f.close()
        return 'Timezone set to '+str(timezone)+', remember to update this when DST starts/ends!'

    def read_time(self, name):
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        found = False
        if len(name) == 0:
            return 'Error: Please enter a user\'s name.'
        for a in data['usertimezones'].keys():
            if name.lower().replace(' ','') in a:
                found = True
                timezone = data['usertimezones'][a]
                time = datetime.datetime.utcnow() + datetime.timedelta(hours=timezone)
                weekday = days[time.weekday()]
                if time.hour < 10:
                    hour_zero = str(0)
                else:
                    hour_zero = ''
                if time.minute < 10:
                    minute_zero = str(0)
                else:
                    minute_zero = ''
                if a[-1] == 's':
                    a = str(a) + '\''
                else:
                    a = str(a) + '\'s'
                return 'It is currently '+weekday+' '+hour_zero+str(time.hour)+':'+minute_zero+str(time.minute)+' in '+a+' time zone.'
        if found == False:
            return 'Either this person has not registered, or such person does not exist.'

    def get_raw_timezone(self,dpl,name):
        self.dpl = dpl
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        if name in data['usertimezones'].keys():
            return data['usertimezones'][name.lower()]
        else:
            return None
