import pickle
import datetime


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
        f = open(self.dpl,'rb')
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
