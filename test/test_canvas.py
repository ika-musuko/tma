import sys
sys.path.append("../src")
import sqlite3
import event
import schedule
import datetime
import canvas
from util import *


with open("sherwyn_key.txt", "r") as f:
    API_KEY = f.readline().strip()

# create some classes
# user id, name, desc, daystr, period_start, period_end, start_time, end_time

classlist = [
             ('0','CMPE102', 'Assembly Language Programming',       'T', '2017-08-22','2017-12-13', '18:00', '20:45')
            ,('0','CMPE120', 'Computer Hardware and Architecture',  'TH','2017-08-22','2017-12-13', '13:30', '14:45')
            ,('0','CMPE131', 'Software Engineering I',              'TH','2017-08-22','2017-12-13', '16:30', '17:45')
            ,('0','CS146',   'Data Structures and Algorithms',      'MW','2017-08-22','2017-12-13', '15:00', '16:15')
            ,('0','CS151',   'Object-Oriented Programming',         'TH','2017-08-22','2017-12-13', '10:30', '11:45')
            ,('0','Dinner',   'Dinner',                         'MWHFSN', None       , None       , '19:00', '19:30')
            ,('0','Dinner',   'Dinner Tuesday',                      'T', None       , None       , '21:30', '22:00')
            ]  
            

# define sleep schedule (also meals are the same i guess lol)
# user id, start_time, end_time
sleeplist = [ ('0', '23:30', '08:30', 'Sleep')
             ,('0', '09:45', '10:15', 'Breakfast')
             ,('0', '12:00', '12:30', 'Lunch')
            ]
# user id, name, desc, start   
userlist = [
             ('0', 'movie with mark', 'see a movie with mark', '2017-10-26 21:00')
            ,('0', 'computer history museum', 'go to the computer history museum because you can', '2017-10-29 11:30')
            ,('0', 'some other thing', 'blah blah', '2017-10-27 2:30')
           ]

## schedule test code 
def convert_recur(elist: list):
    return [event.RecurringEvent( start_time=totime(cl[6])
                              ,end_time=totime(cl[7])
                              ,name=cl[1]
                              ,desc=cl[2]
                              ,period_start=(None if cl[4] is None else todate(cl[4]))
                              ,period_end=(None if cl[5] is None else todate(cl[5]))
                              ,daystr=cl[3]
                              ) for cl in elist]

classevents = convert_recur(classlist)
sleepevents = [event.SleepEvent( start_time=totime(sl[1])
                                ,end_time=totime(sl[2])
                                ,name=sl[3]
                               ) for sl in sleeplist]

userevents = [event.Event( name=ul[1]
                          ,desc=ul[2]
                          ,start=todatetime(ul[3])
                         ) for ul in userlist]
                           
today = datetime.datetime.today()
next_day = datetime.timedelta(days=2)  
end = today+datetime.timedelta(days=2)
                      
schedule = schedule.Schedule(events=classevents+sleepevents+userevents)
schedule.add_from_canvas(API_KEY)
schedule.print_schedule(today, end)
print(canvas.get_courses(API_KEY))
