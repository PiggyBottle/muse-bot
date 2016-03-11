import datetime
import time
import pickle
#from Pastebin import PastebinAPI
import json
import urllib.request
import urllib.parse
import usertimes


class Logger():
    def __init__(self,dpl,lpl):
        self.logstxt = 'D:\Documents\muse-bot\logs.txt'
        self.dpl = dpl
        self.lpl = lpl
        self.empty_time_box = '[' + (' ' * 18) + '|\r\n'
    def log(self, dict):
        dict['time'] = datetime.datetime.utcnow()
        #aparently there is a possibility of having an IO system interrupted error, so trying out this 'loop-until-succeed' approach
        loaded = False
        while loaded == False:
            try:
                f = open(self.lpl, 'rb')
                data = pickle.load(f)
                f.close()
                loaded = True
            except:
                pass
        if not dict['channel'] == None and not dict['private_messaged'] == True:
            data[dict['channel']].append(dict)
            f = open(self.lpl, 'wb')
            pickle.dump(data, f)
            f.close()
    def read(self, dict):
        a = usertimes.TimeZoneCheck()
        tz = a.get_raw_timezone(self.dpl,dict['name'].lower())
        if tz == None:
            dict['message'] = 'Set your timezone first! $settimezone <number>'
            return dict
        f = open(self.lpl, 'rb')
        data = pickle.load(f)
        f.close()
        log = ''
        log_date = None
        log_month = None
        log_year = None
        for a in reversed(data['#nanodesu']):
            buffer = ''
            time_string,time_date,time_month,time_year = self.display_time(a['time'],tz)
            buffer += time_string
            if a['type'] == 'PRIVMSG':
                buffer += '%s|%s\r\n' %(self.display_name(a['name']), a['message'])
            elif a['type'] == 'JOIN':
                buffer += '%s%s has joined the channel.\r\n' %(self.display_name(None), a['name'])
            elif a['type'] == 'PART':
                buffer += '%s%s has parted from the channel.\r\n' %(self.display_name(None), a['name'])
                if a['name'].lower() == dict['name'].lower():
                    log = buffer + log
                    break
            elif a['type'] == 'QUIT':
                buffer += '%s%s has left the channel.\r\n' %(self.display_name(None), a['name'])
                if a['name'].lower() == dict['name'].lower():
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
        dict['message'] = json.loads(response)['paste']['raw']
        return dict
        '''
        f = open(self.logstxt, 'r')
        a = self.pastebin.paste('2333bedc76cd701be6a8526402393da6',f.read(),api_user_key=self.pastebin.generate_user_key('2333bedc76cd701be6a8526402393da6','SoraSky','123456'),paste_private = 'public')
        f.close()
        return a
        '''
    def clear(self):
        f = open(self.lpl, 'wb')
        data = {'#nanodesu':[]}
        pickle.dump(data,f)
        f.close()

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
    f = open('/storage/emulated/0/com.hipipal.qpyplus/scripts3/muse-bot/logs.pickle', 'rb')
    data = pickle.load(f)
    f.close()
    print(len(data['#nanodesu']))
    a = ''
    while a != 'd':
        a = input('write a number, press \'d\' when done.')
        try:
            a = int(a)
            print(data['#nanodesu'][a])
        except:
            pass
    start = input('select starting index')
    end = input('select ending index')
    del data['#nanodesu'][int(start):int(end)]
    print('Length of log is %d' %(len(data['#nanodesu'])))
    a = input('Are you sure?')
    f = open('/storage/emulated/0/com.hipipal.qpyplus/scripts3/muse-bot/logs.pickle', 'wb')
    pickle.dump(data,f)
    f.close()
    print('done')

if __name__ == '__main__':
    clear_log()
