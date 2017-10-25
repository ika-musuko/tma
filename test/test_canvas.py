import sys
sys.path.append("../src")
import sqlite3
import event
import schedule
import datetime
from canvas import *
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
          ]  

# define sleep schedule
# user id, start_time, end_time
sleeplist = [ ('0', '01:30', '09:30') ]
# user id, name, desc, start   
userlist = [
             ('0', 'dinner with mark', 'eat dinner with mark at in-n-out', '2017-10-24 22:00')
            ,('0', 'computer history museum', 'go to the computer history museum because you can', '2017-10-29 11:30')
            ,('0', 'some other thing', 'blah blah', '2017-10-24 23:30')
           ]

## schedule test code 
classevents = [event.RecurringEvent( start_time=totime(cl[6])
                              ,end_time=totime(cl[7])
                              ,name=cl[1]
                              ,desc=cl[2]
                              ,period_start=todate(cl[4])
                              ,period_end=todate(cl[5])
                              ,daystr=cl[3]
                              ) for cl in classlist]
    
dueevents = get_from_canvas(API_KEY)

sleepevents = [event.SleepEvent( start_time=totime(sl[1])
                                ,end_time=totime(sl[2])
                               ) for sl in sleeplist]

userevents = [event.Event( name=ul[1]
                          ,desc=ul[2]
                          ,start=todatetime(ul[3])
                         ) for ul in userlist]
                           
today = datetime.datetime.today()
next_day = datetime.timedelta(days=2)  
end = today+datetime.timedelta(days=2)                      
#schedule = schedule.Schedule(events=classevents+dueevents+sleepevents, start=today+next_day, end=end)
schedule = schedule.Schedule(events=classevents+dueevents+sleepevents+userevents)
schedule.print_schedule(today, end)
