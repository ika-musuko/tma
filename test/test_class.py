import sys
sys.path.append("../src")
import sqlite3
import event
import schedule
import datetime

# create some classes
classlist = [
             ('0','CMPE102', 'Assembly Language Programming',       'T', '2017-08-22','2017-12-13', '18:00', '20:45')
            ,('0','CMPE120', 'Computer Hardware and Architecture',  'TH','2017-08-22','2017-12-13', '13:30', '14:45')
            ,('0','CMPE131', 'Software Engineering I',              'TH','2017-08-22','2017-12-13', '16:30', '17:45')
            ,('0','CS146',   'Data Structures and Algorithms',      'MW','2017-08-22','2017-12-13', '15:00', '16:15')
            ,('0','CS151',   'Object-Oriented Programming',         'TH','2017-08-22','2017-12-13', '10:30', '11:45')      
          ]      



# conn = sqlite3.connect("classtest.db")
# c = conn.cursor()

# sql creation code
# c.execute('''CREATE TABLE classes
             # ( 
                   # id integer
                 # , name text
                 # , desc text
                 # , days text
                 # , period_start text
                 # , period_end text
                 # , start_time text
                 # , end_time text
             # )'''
          # )
          
   
# c.executemany("INSERT INTO classes VALUES (?,?,?,?,?,?,?,?)", classlist)
# conn.commit()

# convert a datestring into a datetime.date
def todate(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()

# convert a timestring into a datetime.time
def totime(s: str) -> datetime.time:
    return datetime.datetime.strptime(s, "%H:%M").time()

## schedule test code 
classevents = [event.RecurringEvent( start_time=totime(cl[6])
                              ,end_time=totime(cl[7])
                              ,name=cl[1]
                              ,desc=cl[2]
                              ,period_start=todate(cl[4])
                              ,period_end=todate(cl[5])
                              ,daystr=cl[3]
                              ) for cl in classlist]
    
schedule = schedule.Schedule(events=classevents)
today = datetime.datetime.today()
schedule.print_schedule(today, today+datetime.timedelta(days=4))