import event
from eventqueue import EventQueue
import datetime
import sqlite3
import heapq
import operator
from collections import deque

'''
    schedule.py
'''
def combine(date: datetime.date, time: datetime.time) -> datetime.datetime:
    '''
    wrapper around datetime.datetime.combine()
    '''
    return datetime.datetime.combine(date, time)
    
class Region:
    DEFAULT_START = datetime.datetime(2017, 1, 1, 0, 0, 0)
    DEFAULT_END = datetime.datetime(2099, 1, 1, 0, 0, 0)
    DEFAULT_DURATION = datetime.timedelta(hours=2)
    '''
    the start and end boundaries of a Schedule (for viewing)
    Attributes:
        start (datetime.datetime): starting datetime
        end (datetime.datetime): ending datetime
    '''
    def __init__(self
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                    , duration: datetime.timedelta=None
                ):
        if duration is not None:
            end = start + duration
        
        # verify that start is chronologically before end
        elif start is not None and end is not None and start > end:
            start = Region.DEFAULT_START 
            end = start + Region.DEFAULT_DURATION
            
        self.start = start
        self.end = end
        
    def empty(self):
        return self.start is None and self.end is None
        
        
    def fill(self):
        '''
        make this Region DEFAULT_DURATION long if either the start or end members are None
        '''
        if self.empty():
            self.start = Region.DEFAULT_START
            self.end = Region.DEFAULT_END

        elif self.end is None:
            self.end = self.start + Region.DEFAULT_DURATION
        
        elif start is None:
            self.start = self.end - Region.DEFAULT_DURATION
            
        else:
            return
            
    def __lt__(self, other):
        return self.start < other.start
        
    def __str__(self):
        return "Region: start %s end %s" % (self.start, self.end)
        
class ScheduleEvent(event.Event):
    '''
    Schedule will convert every element in its user_events into this type of event
        
    combining a date and time: https://vgy.me/LLwv0g.png
    
    Parent:
        Event
    Attributes:
        extra_info: other information such as due date for DueEvents and recurrence for RecurringEvents
    '''
    DAY_NAMES = {
            0 : "Monday",
            1 : "Tuesday",
            2 : "Wednesday",
            3 : "Thursday",
            4 : "Friday",
            5 : "Saturday",
            6 : "Sunday"
    }
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                    , extra_info: str=""
                ):
        event.Event.__init__(self=self, name=name, desc=desc, priority=priority, start=start, end=end)
        self.extra_info = extra_info
        
    def __str__(self):
        return '''{name}
        {desc}
        {dow}
        {start}
        {end}
        {ei}
        '''.format(name=self.name, desc=self.desc, dow=ScheduleEvent.DAY_NAMES[self.start.weekday()], start=hm(self.start), end=hm(self.end), ei=self.extra_info)
    
    def __repr__(self):
        return ": ".join(("ScheduleEvent", str(self.__dict__)))

def hm(dt: datetime.datetime) -> str:
    '''
    removes seconds from datetime.datetime print
    '''
    return "{y}-{m:02d}-{d:02d} {h:02d}:{min:02d}".format(y=dt.year, m=dt.month, d=dt.day, h=dt.hour, min=dt.minute)
    
def weeklydays(start: datetime.date, end: datetime.date=None, dayofweek: str="") -> "generator of datetime.date":
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
    
class Schedule:
    zerotime = datetime.time()
    def __init__(self
                    , events: list=[]
                    , region: Region=Region()
                ):
        '''
        create a schedule from a list of Event
        Attributes:
            actual_events (list of ScheduleEvent): every user_event will get converted into a ScheduleEvent and scheduled according to the current 
            event_queue (EventQueue): every event
            region (Region): the start and end dates to push actual_events in
        '''
        # initialize arguments
        self.actual_events = []
        self.region = region
        self.region.fill()
        self.event_queue = EventQueue(events)
        self.update()
      
    def update(self):
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        self.actual_events = [] # add events to this
        generated_events = []  # all of the generated events
        earliest_free_region = Region(Region.DEFAULT_START)
        earliest_free_region.fill()
        earliest_event = None
        second_earliest_event = None 
        used_earliest_region = True
        
        for e in self.event_queue:
            extra_info = ""
            # generate corresponding events in region 
            ## if the event is an event.RecurringEvent, generate all recurring events in self.region
           # print("%s %s %s id: %s" % (date, start_datetime, end_datetime, e.id))
            if isinstance(e, event.RecurringEvent):
                # generate ScheduleEvents per weekday
                for day in e.days:
                    for date in weeklydays(e.period_start, e.period_end, day): # the region is only e.period_start and e.period_end
                        # make a date for the new ScheduleEvent
                        start_datetime = combine(date, e.start_time)
                        end_datetime = combine(date, e.end_time)   
                        # convert the event into a ScheduleEvent and append
                        extra_info = "Recurring Event: %s start: %02d:%02d end: %02d:%02d" % (   e.day_names
                                                                                       , start_datetime.hour
                                                                                       , start_datetime.minute
                                                                                       , end_datetime.hour
                                                                                       , end_datetime.minute
                                                                                     )
                        
                        se = ScheduleEvent(e.name, e.desc, e.priority, start_datetime, end_datetime, extra_info)
                        heapq.heappush(generated_events, (se.start, se)) # push in sorted order, by start time
                        self.actual_events.append(se)
            
            ## if the event is an event.TaskEvent, generate events according to earliest_free_region          
            elif isinstance(e, event.TaskEvent):
                # 1. find the earliest event's end time and second earliest's start time
                # 2. figure out whether current earliest region or event free region is earlier and use the earliest one of the two
                # 3. create a region using earliest free region and the current TaskEvent's duration
                # 4. use the region to add to self.actual_events and generated_events
                # 5. set the earliest free region to the next free region
                
                # step 1
                if used_earliest_region:
                    if(len(generated_events) > 0):
                        earliest_event = heapq.heappop(generated_events)[1]
                    if(len(generated_events) > 0):
                        second_earliest_event = heapq.heappop(generated_events)[1]
                event_free_region = Region(earliest_event.end, second_earliest_event.start)
                
                # step 2/3
                if earliest_free_region > event_free_region:
                    earliest_free_region = event_region # step 3 reassign
                    used_earliest_region = False
                else:
                    used_earliest_region = True
                
                # step 4
                extra_info = "Task, "
                if isinstance(e, event.DueEvent):
                    extra_info = ''.join((extra_info,"Due: %s" % e.due))
                event_end_datetime = earliest_free_region.start + datetime.timedelta(hours=e.duration)
                self.actual_events(ScheduleEvent( e.name
                                                , e.desc
                                                , e.priority
                                                , start=earliest_free_region.start
                                                , end=event_end_datetime
                                                , extra_info=extra_info
                                                ))
                
                # step 5
                earliest_free_region = Region(event_end_datetime, None)
                earliest_free_region.fill()
                              
            ## this is a simple Event so just map it 1 to 1 to a Schedule
            else:
                self.actual_events.append(ScheduleEvent(e.name, e.desc, e.priority, e.start, e.end, extra_info))
            
        # sort actual_events by ScheduleEvent.start
        self.actual_events.sort(key=operator.attrgetter("start"))
        
    def add_event(self, e: event.Event):
        '''
        add event
        '''
        self.event_queue.push(e)
    
    
    # def add_from_sql(self, conn: sqlite3.Connection, table: str):
        # '''
        # add events from sql table to the event queue
        # table is the table name
        # filter is an sql filter 
        # '''
        # params = (table, filter)
        # c = conn.cursor()
        # execstr = ("SELECT * FROM %s" % table)
        # for row in c.execute(execstr):
            
    def delete_event(self, id: int) -> bool:
        '''
        delete Event by id
        '''
        self.event_queue.delete_by_id(id)
    
    def get_events_in_region(self, start, end):
        return [se for se in self.actual_events if start <= se.start and end >= se.end]
        
    def print_schedule(self
                            , start: datetime.datetime=None
                            , end: datetime.datetime=None
                       ):
        if start is None:
            start = self.region.start
        if end is None:
            end = self.region.end    
        
        getactual = self.get_events_in_region(start, end)
        for se in getactual:
            print(se)
        