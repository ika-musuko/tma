import datetime
from app.scheduler import event
from sortedcontainers import SortedList

'''
    util.py

    assorted utility functions used throughout the system
'''

def todatetime(s: str) -> datetime.datetime:
    '''
    convert a datetimestring into a datetime.datetime
    '''
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")

def todate(s: str) -> datetime.date:
    '''
    convert a datestring into a datetime.date
    '''
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()

def totime(s: str) -> datetime.time:
    '''
    convert a timestring into a datetime.time
    '''
    return datetime.datetime.strptime(s, "%H:%M").time()
    
def tohours(td: datetime.timedelta) -> float:
    '''
    converts a timedelta into hours as a float
    '''
    return td / datetime.timedelta(hours=1)

def tominutes(td: datetime.timedelta) -> int:
    '''
    converts a timedelta into minutes as an int
    '''
    return td // datetime.timedelta(minutes=1)
    
def combine(date: datetime.date, time: datetime.time) -> datetime.datetime:
    '''
    wrapper around datetime.datetime.combine()
    '''
    return datetime.datetime.combine(date, time)


def weeklydays(start: datetime.date, end: datetime.date=None, dayofweek: str="") -> 'generator of datetime.date':
    '''
    generator of list of days in week from dayofweek in region
    ex:
        weeklydays(r, "T") -> generates every Tuesday in r 
    '''
    current_date = start
    next_day_increment = ({d: i for i, d in enumerate("MTWHFSN")}[dayofweek] - start.weekday()) % 7
    current_date += datetime.timedelta(days=next_day_increment) # go to the next day that matches dayofweek
    if end is None:
        yield current_date
        current_date += datetime.timedelta(days=7) # go to next week
    else:
        while current_date < end:
            yield current_date
            current_date += datetime.timedelta(days=7) # go to next week
            
def hm(dt: datetime.datetime) -> str:
    '''
    removes seconds from datetime.datetime string
    ex:
        2017-10-22 21:21
    :param dt: the datetime to convert
    :return type: string of the datetime without the seconds
    '''
    return "{y}-{m:02d}-{d:02d} {h:02d}:{min:02d}".format(y=dt.year, m=dt.month, d=dt.day, h=dt.hour, min=dt.minute)

def none(things: 'iterable') -> bool:
    return None in things    
 
def comp(x, y) -> None:
    '''
    shows the results of <. =. and >
    '''
    print("%s %s" % (x, y))
    print("<<<<: %s" % (x < y))           
    print("=== : %s" % (x == y))
    print(">>>>: %s" % (x > y))    

def sort_extend(sl: SortedList, things: iter) -> None:
    '''
    add all things to sl in place
    :param sl: the SortedList to add to
    :param things: iterable of things to add
    '''
    for t in things:
        sl.add(t)
