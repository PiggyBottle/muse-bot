import datetime
import time
import pickle
#from Pastebin import PastebinAPI
import json
import urllib.request
import urllib.parse
import usertimes
import pastee #This is the back up for paste.ee site when it's down
import MySQLdb
import copy


class Logger():
    def __init__(self,dpl,lpl,config):
        self.dpl = dpl
        self.lpl = lpl
        self.config = config
        self.empty_time_box = '[' + (' ' * 18) + '|\r\n'
        loaded = False
        while loaded == False:
            try:
                f = open(self.lpl, 'rb')
                self.data = pickle.load(f)
                f.close()
                loaded = True
            except:
                pass
    def log(self, event, namelist):
        #In an attempt to fix aliasing issues, content is now a copy of a the IRC event.
        content = copy.deepcopy(event)
        content['time'] = datetime.datetime.utcnow()
        #aparently there is a possibility of having an IO system interrupted error, so trying out this 'loop-until-succeed' approach
        if content['type'] == 'QUIT':
            #because the 'QUIT' action applies to multiple channels.
            for a in namelist.keys():
                if content['name'] in namelist[a]:
                    self.data[a].append(content)
            f = open(self.lpl, 'wb')
            pickle.dump(self.data, f)
            f.close()
        elif not content['channel'] == None and not content['private_messaged'] == True:
            if not content['channel'] in self.data.keys():
                self.data[content['channel']] = []
            self.data[content['channel']].append(content)
            f = open(self.lpl, 'wb')
            pickle.dump(self.data, f)
            f.close()
    def read(self, content):
        a = usertimes.TimeZoneCheck()
        tz = a.get_raw_timezone(self.dpl,content['name'].lower())
        if tz == None:
            content['message'] = 'Set your timezone first! $settimezone <number>'
            return content
        f = open(self.lpl, 'rb')
        data = pickle.load(f)
        f.close()
        log = ''
        log_date = None
        log_month = None
        log_year = None
        channel_to_search = ''
        if not content['channel'] in data.keys():
            channel_to_search = '#nanodesu'
        else:
            channel_to_search = content['channel']
        for a in reversed(data[channel_to_search]):
            buffer = ''
            time_string,time_date,time_month,time_year = self.display_time(a['time'],tz)
            buffer += time_string
            if a['type'] == 'PRIVMSG':
                buffer += '%s|%s\r\n' %(self.display_name(a['name']), a['message'])
            elif a['type'] == 'JOIN':
                buffer += '%s%s has joined the channel.\r\n' %(self.display_name(None), a['name'])
            elif a['type'] == 'PART':
                buffer += '%s%s has parted from the channel.\r\n' %(self.display_name(None), a['name'])
                if a['name'].lower() == content['name'].lower():
                    log = buffer + log
                    break
            elif a['type'] == 'QUIT':
                buffer += '%s%s has left the channel.\r\n' %(self.display_name(None), a['name'])
                if a['name'].lower() == content['name'].lower():
                    log = buffer + log
                    break
            elif a['type'] == 'NICK':
                buffer += '%s%s has changed his nick to %s.\r\n' %(self.display_name(None), a['name'],a['message'])
            elif a['type'] == 'KICK':
                buffer += '%s%s %s.\r\n' %(self.display_name(None), a['name'], a['message'] )
            if log_date == None:
                log_date = time_date
                log_month = time_month
                log_year = time_year
            elif log_date != None and log_date != time_date:
                buffer += self.empty_time_box + '[----%s.%s.%d----|\r\n' %(log_date,log_month,log_year) + self.empty_time_box
                log_date = time_date
                log_month = time_month
                log_year = time_year
            log = buffer + log
        log = '[----%s.%s.%d----|\r\n' %(log_date,log_month,log_year) + log

        ###This is for MySQL
        db = MySQLdb.connect('localhost', self.config['sql']['user'], self.config['sql']['password'], 'irclog',charset='utf8')

        cursor = db.cursor()

        sql = "INSERT INTO irclog_irclog (content) VALUES (%s)"

        succeeded = False
        try:
            cursor.execute(sql,[log])
            db.commit()
            succeeded = True
        except Exception as e:
            db.rollback()
            print('failed. Exception: ' + str(e))
            db.close()

        if succeeded:
            cursor.execute('SELECT LAST_INSERT_ID()')
            results = cursor.fetchall()
            content['message'] = 'http://muse-chan.flu.cc/irclog/'+ str(results[0][0])
            db.close()
            return content

        ###########

        ###This is for paste.ee client
        '''
        a = {'key':'808f1be384f08c1d10806809193fe66b','description':'test', 'paste':log}
        json.dumps(a)
        url = 'https://paste.ee/api'
        b = urllib.parse.urlencode(a).encode('utf-8')
        f.close()
        try:
            request = urllib.request.urlopen(url, b)
        except http.client.HTTPException as e:
            print(e)
        response = request.read().decode()
        content['message'] = json.loads(response)['paste']['raw']
        return content
        '''
        ##########
        
        ###This is for pastee client
        '''
        client = pastee.PasteClient()
        content['message'] = str(client.paste(log.encode()))
        return content
        '''
        ##########

        ###This is for pastebin
        '''
        f = open(self.logstxt, 'r')
        a = self.pastebin.paste('2333bedc76cd701be6a8526402393da6',f.read(),api_user_key=self.pastebin.generate_user_key('2333bedc76cd701be6a8526402393da6','SoraSky','123456'),paste_private = 'public')
        f.close()
        return a
        '''
        ##########
    def display_time(self,time,tz):
        time += datetime.timedelta(hours=tz)
        if time.hour < 10:
            hour_zero = str(0)
        else:
            hour_zero = ''
        if time.minute < 10:
            minute_zero = str(0)
        else:
            minute_zero = ''
        day_zero = str(time.day)
        if len(day_zero) < 2:
            day_zero = '0' + day_zero
        month_zero = str(time.month)
        if len(month_zero) < 2:
            month_zero = '0' + month_zero
        return '[%s%d:%s%d]' %(hour_zero, time.hour, minute_zero, time.minute), day_zero, month_zero, time.year
    def display_name(self, name):
        if name == None:    #for channel parts, quits, joins, etc
            return (' ' * 12)+'|'
        space = ''
        if len(name) < 12:
            space = ' ' * (12 - len(name))
        if len(name) > 12:
            name = name[:12]
        return space + name

####log clearer###
def clear_log():
    f = open('logs.pickle', 'rb')
    data = pickle.load(f)
    f.close()
    for channel in data.keys():
        print(str(channel))
        print(len(data[channel]))
        a = ''
        while a != 'd':
            a = input('write a number, press \'d\' when done.')
            try:
                a = int(a)
                print(data[channel][a])
            except:
                pass
        start = input('select starting index')
        end = input('select ending index')
        del data[channel][int(start):int(end)]
        print('Length of log is %d' %(len(data[channel])))
        a = input('Are you sure?')
    f = open('logs.pickle', 'wb')
    pickle.dump(data,f)
    f.close()
    print('done')

if __name__ == '__main__':
    clear_log()
