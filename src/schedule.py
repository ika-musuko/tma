import event
from eventqueue import EventQueue
import datetime
import dateutil.parser
import sqlite3
from sortedcontainers import SortedList, SortedListWithKey
import operator
import json
import requests
from collections import deque
from util import *

'''
    schedule.py
'''

class Region:
    DEFAULT_START = datetime.datetime(2017, 10, 1, 0, 0, 0)
    DEFAULT_END = datetime.datetime(2018, 1, 1, 0, 0, 0)
    DEFAULT_DURATION = datetime.timedelta(hours=2)
    '''
    the start and end boundaries of a Schedule (for viewing)
    :param start: starting datetime
    :param end: ending datetime
    '''
    def __init__(self
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                    , duration: datetime.timedelta=None
                ):
        if duration is not None:
            end = start + duration
        
        # verify that start is chronologically before end
        elif (not none((start, end))) and start > end:
            start = Region.DEFAULT_START 
            end = start + Region.DEFAULT_DURATION
            
        self.start = start
        self.end = end
        
    def empty(self):
        return none((self.start, self.end))
        
        
    def fill(self):
        '''
        make this Region DEFAULT_DURATION long if either the start or end members are None
        '''
        if self.empty():
            self.start = Region.DEFAULT_START
            self.end = Region.DEFAULT_END
        
        elif self.end is None:
            self.end = self.start + Region.DEFAULT_DURATION
        
        elif self.start is None:
            self.start = self.end - Region.DEFAULT_DURATION
            
        else:
            return
            
    def __lt__(self, other):
        return self.start < other.start
        
    def __gt__(self, other):
        return self.start > other.start    
        
    def __eq__(self, other):
        return self.start == other.start   
        
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
        {dow}
        {start}
        {end}
        {ei}
        '''.format(name=self.name, dow=ScheduleEvent.DAY_NAMES[self.start.weekday()], start=hm(self.start), end=hm(self.end), ei=self.extra_info)
    
    def __repr__(self):
        return ": ".join(("ScheduleEvent", str(self.__dict__)))

class Schedule:
    zerotime = datetime.time()
    def __init__(self
                    , events: list=[]
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                ):
        '''
        Schedule constructor
        create a schedule from a list of Event
        :param actual_events (list of ScheduleEvent): every user_event will get converted into a ScheduleEvent and scheduled according to the current 
        :param event_queue (EventQueue): every event
        :param region (Region): the start and end dates to push actual_events in
        '''
        # initialize arguments
        self.actual_events = []
        self.region = Region(start, end)
        self.region.fill()
        self.event_queue = EventQueue(events)
        print(self.event_queue)
        self.update()


    def update(self) -> None:
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        # if the current region.start is earlier than today, make the earliest free region's start earlier than today. else, maintain the current region.start for earliest free region
        today = datetime.datetime.today()
        self.earliest_free_region = Region(today if self.region.start < today else self.region.start, self.region.end)
        print(self.earliest_free_region)
        self.generated_events = SortedList()
        self.actual_events = SortedList()

        # go through all of the events on the queue...
        for e in self.event_queue:
            # se is an iterable of ScheduleEvent
            if isinstance(e, event.RecurringEvent):
                se = self.generate_recurring_events(e)
            elif isinstance(e, event.TaskEvent):
                se = self.generate_task_events(e)
            # this is just a normal event so turn it into a tuple of 1 element to extend
            else:
                se = (ScheduleEvent(name=e.name, desc=e.desc, start=e.start, end=e.end, extra_info="USER EVENT"),)
            self.push_generated_events(se, today)
            sort_extend(self.actual_events, se) # add all of the ScheduleEvents
    
    def push_generated_events(self, se: list, today: datetime.datetime) -> None:
        '''
        push generated events only if they happened after today
        '''
        sort_extend(self.generated_events, [s for s in se if s.start >= today])

    def generate_recurring_events(self, re: event.RecurringEvent) -> 'SortedList of event.RecurringEvent':
        '''
        convert a RecurringEvent into a bunch of ScheduleEvents from re.period_start to re.period_end
        if re.period_start is None, use self.region.start as the beginning period
        generate ScheduleEvent.start and ScheduleEvent.end using util.weeklydays()
        :param re: the RecurringEvent to generate from
        '''
        se = SortedList()
        for d in re.days:
            for day in weeklydays(self.region.start if re.period_start is None else re.period_start, self.region.end if re.period_end is None else re.period_end, d):
                # make dates from the RecurringEvent's start_time and end_time
                start_datetime = combine(day, re.start_time)
                # if re is a SleepEvent and the start_time is after the end_time, advance to the next day
                end_datetime = combine(day+datetime.timedelta(days=int(isinstance(re, event.SleepEvent) and re.start_time > re.end_time)), re.end_time)
                
                re_extra_info = "SLEEP Event: bed: %s wake: %s" % (re.start_time, re.end_time) if isinstance(re, event.SleepEvent) else  "Recurring Event: %s start: %02d:%02d end: %02d:%02d" % (   re.day_names
                                                                                       , start_datetime.hour
                                                                                       , start_datetime.minute
                                                                                       , end_datetime.hour
                                                                                       , end_datetime.minute
                                                                                     ) 
                # generate a ScheduleEvent
                new_se = ScheduleEvent(name=re.name, desc=re.desc, start=start_datetime, end=end_datetime, extra_info=re_extra_info)
                se.add(new_se)
        return se

    def generate_task_events(self, te: event.TaskEvent) -> ('generator of event.TaskEvent', Region, 'SortedList of ScheduleEvent'):
        '''
        convert a TaskEvent into a bunch of ScheduleEvents
        :param te: the TaskEvent to generate from
        '''    

        ### AUTOMATIC SCHEDULE GENERATING ALGORITHM
        ## fix conflicts between events by checking if the start and end datetimes are inside another existing event, and readjusting the start and end times to match the boundaries of the conflicting events
        ## future optimization: stuff the start and end checker into one for loop?
        # set the start time
        start_datetime = self.earliest_free_region.start # use the start of the earliest_free_region
        for ge in self.generated_events:
            if ge.start > start_datetime:
                # self.generated_events is sorted so we can break out early if we go too far
                break
            # if there's a conflict, set the new start to the end of the conflicting event
            elif ge.start <= start_datetime < ge.end:
                start_datetime = ge.end
                break
        # set the end time
        end_datetime = start_datetime+te.duration # the event will end according to the duration of the event specified in the class
        for ge in self.generated_events:
            if ge.start > end_datetime:
                break
            # if there's a conflict, set the new end to the start of the conflicting event
            elif ge.start <= end_datetime < ge.end:
                end_datetime = ge.start
         
        te_extra_info = "DUE EVENT: due: %s" % (te.due) if isinstance(te, event.DueEvent) else "Task Event"
        new_se = ScheduleEvent(name=te.name, desc=te.desc, start=start_datetime, end=end_datetime, extra_info = te_extra_info) 
        self.earliest_free_region = Region(new_se.end, self.region.end) # set the free region to after the new event was created
        #print("post: %s" % self.earliest_free_region)
        return [new_se]
    
    def add_event(self, e: event.Event) -> None:
        '''
        add event
        :param e: the Event to add
        '''
        self.event_queue.push(e)
    
    
    # def add_from_sql(self, conn: sqlite3.Connection, table: str) -> None:
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
        :param id: look for the event with this id to delete
        todo - after the UI is properly conceptualized, these params might have to be changed?
        '''
        self.event_queue.delete_by_id(id)
    
    def get_events_in_region(self, start: datetime.datetime, end: datetime.datetime) -> 'generator of ScheduleEvent':
        '''
        return a generator of every actual event from start to end
        :param start: start generator from here
        :param end: end generator here
        '''
        return (se for se in self.actual_events if start <= se.start <= end)
        
    def print_schedule(self
                            , start: datetime.datetime=None
                            , end: datetime.datetime=None
                       ) -> None:
        '''
        print out the schedule to the terminal from start to end
        :param start: start printing from here
        :param end: end printing here
        '''
        if start is None:
            start = self.region.start
        if end is None:
            end = self.region.end    
       
        getactual = self.get_events_in_region(start, end)
        for se in getactual:
            print(str(se))
    
