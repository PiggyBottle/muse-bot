import pickle
import datetime
import re
import datetime
from html.parser import HTMLParser
import urllib.request


class AnimeTiming():
    def __init__(self):
        pass
    def execute(self, w, datapicklelocation):
        self.dpl = datapicklelocation
        self.word = w
        self.time_left(self.word)
        try:
            self.days, self.hours, self.minutes, self.title = self.time_left(self.word)
            if self.days == 6:
                return self.title+' subs have just recently been released. Check it out now!'
            else:
                return str('%s subs will be released in %d days, %d hours and %d minutes.' %(self.title, self.days,self.hours,self.minutes))
        except:
            return 'Error: Anime not found'
        
    def day_counter(self,date):
        counter = 0
        start_counting = False
        current_weekday = datetime.datetime.utcnow().isoweekday()
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
        f = open(self.dpl,'rb')
        anime_showtime = pickle.load(f)['anime_showtime']
        f.close()
        for a in anime_showtime.keys():
            if w.lower() in a:
                days =self.day_counter(anime_showtime[a][0])
                hours = anime_showtime[a][1] - datetime.datetime.utcnow().hour
                minutes = anime_showtime[a][2] - datetime.datetime.utcnow().minute
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


    def check_website(self):
        try:
            url = 'http://horriblesubs.info/release-schedule/'
            url2 = 'http://www.timeanddate.com/time/zone/usa/los-angeles'

            # Get UTC offset of HorribleSubs's servers as an integer
             
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
            req = urllib.request.Request(url2, headers = headers)
            resp = urllib.request.urlopen(req)
            respData = resp.read().decode()
            #Note that this is still a string!
            timezoneoffset = re.search(r'-[0-9] hours', respData).group()[1]

            #Get data from HorribleSubs's site

            req = urllib.request.Request(url, headers = headers)
            resp = urllib.request.urlopen(req)
            respData = resp.read().decode()
            string = respData.split('\n')
            anime_showtimes = self.parseHTML(string,timezoneoffset)
            return anime_showtimes
        except Exception as e:
            print(str(e))
    def parseHTML(self,string,timezoneoffset):
        h = HTMLParser()
        anime_showtimes = {}
        start = False
        for line in string:
            try:
                if not line.startswith('<h2 class="weekday">') and not start:
                    pass
                elif re.search(r'<td class="schedule-page-show">.*>(.*)</a>', line) != None:
                    title = h.unescape(re.search(r'<td class="schedule-page-show">.*>(.*)</a>', line).group(1))
                elif re.search(r'<h2 class="weekday">(.*)</h2>',line) != None:
                    weekday = h.unescape(re.search(r'<h2 class="weekday">(.*)</h2>',line).group(1))
                    if weekday == 'To be scheduled':
                        break
                    elif not start:
                        start = True
                    for i,a in enumerate(['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']):
                        if weekday == a:
                            weekday = i
                            break
                elif re.search(r'<td class="schedule-time">(\d\d:\d\d)</td>',line) != None:
                    time = h.unescape(re.search(r'<td class="schedule-time">(\d\d:\d\d)</td>',line).group(1))
                    time_object = datetime.datetime(2016,5,8+weekday,int(time[0:2]),int(time[3:5])) + datetime.timedelta(hours=int(timezoneoffset))
                    anime_showtimes[title.lower()] = [time_object.isoweekday(),time_object.hour,time_object.minute,title]
            except Exception as e:
                print(str(e))
        return anime_showtimes
