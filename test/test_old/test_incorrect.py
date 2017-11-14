import sys
sys.path.append("../src")
import sqlite3
import event
import schedule
import datetime
from canvas import *
from util import *

# create some classes
# user id, name, desc, daystr, period_start, period_end, start_time, end_time
classlist = [
          ]  

# define sleep schedule
# user id, start_time, end_time
sleeplist = []
# create some things to do
# user id, name, desc, due, priority, done
duelist = [ 
          ]
# user id, name, desc, start   
userlist = [
              ('0', 'EVENT 1', 'e1', '2017-10-24 21:00')
             ,('0', 'EVENT 2', 'e2', '2017-10-24 21:00')
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
    
dueevents = [event.DueEvent( name=dl[1]
                            ,desc=dl[2]
                            ,due=todatetime(dl[3])
                            ,priority=dl[4]
                            ,done=dl[5] 
                           ) for dl in duelist]
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
schedule.print_schedule(datetime.datetime(2017, 10, 24, 21, 0, 0), datetime.datetime(2017, 10, 24, 23, 59, 0))
