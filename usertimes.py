import datetime, time, pickle, re, string

days = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]

class TimeZoneCheck():
    def __init__(self):
        pass
    def execute(self, dict, dpl):
        self.dict = dict
        self.word = self.dict['message']
        self.name = self.dict['name']
        self.dpl = dpl

        #Three types of commands get passed into this class.
        #$settimezone sets the UTC timezone for the user,
        #$time <nick> calls the current time at <nick>'s loaction, and
        #$time calls current time at caller's location.
        if self.word.startswith('$settimezone '):
            return self.set_time(self.name, self.word[13:])
        elif self.word.startswith('$time '):
            return self.read_time(self.word[6:])
        elif self.word == '$time':
            return self.read_time(self.name)

    def set_time(self, name, tz):
        #Brute force technique to allow only valid time zones.
        if tz not in ['-12','-11','-10','-9.5','-9','-8.5','-8','-7','-6','-5','-5','-4','-3.5','-3','-2','-1','0','1','2','3','3','4','4.5','5','5.5','5.75','6','6.5','7','8','8.5','8.75','9','9.5','10','10.5','11','12','12.75','13','14']:
            return 'Invalid Time Zone'
        try:
            timezone = float(tz)
        except:
            return 'Error, that is not a number!'

        #From now on, use timezone instead of 'tz'
        #UTC timezones cannot be <-12 and >14
        if not ((timezone >= -12) and (timezone <= 14)):
            return 'Error: Invalid time zone.'
        
        #Load timezone information into 'data'
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        checktext = '^' + name + '$'
        check = re.compile(checktext, re.IGNORECASE)

        #If user has set his timezone before, replace old timezone with new
        #Else, create a new entry in the pickle
        for user in data['usertimezones'].keys():
            if check.match(user):
                data['usertimezones'][user] = timezone
        else:
            data['usertimezones'][name] = timezone

        #Save data with new timezone information
        f = open(self.dpl,'wb')
        pickle.dump(data,f)
        f.close()

        return 'Timezone set to '+str(timezone)+', remember to update this when DST starts/ends!'

    def read_time(self, name):
        #Preventing spaces from being included in the 'name'
        name = name.replace(' ','')

        #Load timezone information into 'data'
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()

        #Making sure that nick does not contain invalid characters
        if len(name) == 0:
            return 'Error: Please enter a user\'s name.'
        if not re.match("^[A-Za-z0-9_\\\[\]{}^`|-]*$", name):
            return 'Error: Improper character(s) input.'
        name = name.replace('[', '\[')
        name = name.replace(']', '\]')
        name = name.replace('^', '\^')
        name = name.replace('\\', "\\")
        checktext = '\S*' + name + '\S*'
        check = re.compile(checktext, re.IGNORECASE)

        #Begin search for nick
        found = False
        for user in data['usertimezones'].keys():
            if check.match(user):
                found = True
                timezone = data['usertimezones'][user]
                time = datetime.datetime.utcnow() + datetime.timedelta(hours=timezone)
                weekday = days[time.weekday()]

                #These ensure that the time format comes out as 09:05
                #instead of 9:5
                if time.hour < 10:
                    hour_zero = str(0)
                else:
                    hour_zero = ''
                if time.minute < 10:
                    minute_zero = str(0)
                else:
                    minute_zero = ''

                #This ensures that names ending with 's' get an apostrophe
                #and names that do not will get 's
                if user[-1] == 's':
                    user = str(user) + '\''
                else:
                    user = str(user) + '\'s'
                return 'It is currently '+weekday+' '+hour_zero+str(time.hour)+':'+minute_zero+str(time.minute)+' in '+user+' time zone.'
        if found == False:
            return 'Either this person has not registered, or such person does not exist.'


    #This function is used by logger.py that gives the raw timezone number
    #for log-reading
    def get_raw_timezone(self,dpl,name):
        self.dpl = dpl
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        checktext = '\S*' + name + '\S*'
        check = re.compile(checktext, re.IGNORECASE)
        for nickname in data['usertimezones'].keys():
            if check.match(nickname):
                return data['usertimezones'][nickname]
        else:
            return None
