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
    DEFAULT_END = datetime.datetime(2099, 1, 1, 0, 0, 0)
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
        {desc}
        {dow}
        {start}
        {end}
        {ei}
        '''.format(name=self.name, desc=self.desc, dow=ScheduleEvent.DAY_NAMES[self.start.weekday()], start=hm(self.start), end=hm(self.end), ei=self.extra_info)
    
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
        self.update()


    def update(self) -> None:
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        # if the current region.start is earlier than today, make the earliest free region's start earlier than today. else, maintain the current region.start for earliest free region
        today = datetime.datetime.today()
        self.earliest_free_region = Region(today if self.region.start < today else self.region.start, self.region.end)
        self.generated_events = SortedList()
        
        # go through all of the events on the queue...
        for e in self.event_queue:
            # se is an iterable of ScheduleEvent
            if isinstance(e, event.RecurringEvent):
                se = self.recurring_events_gen(e)
                sort_extend(self.generated_events, se)
            elif isinstance(e, event.TaskEvent):
                se = self.task_events_gen(e)
                sort_extend(self.generated_events, se)
            # this is just a normal event so turn it into a tuple of 1 element to extend
            else:
                se = (ScheduleEvent(name=e.name, desc=e.desc, start=e.start, end=e.end, extra_info="USER EVENT"),)
            self.actual_events.extend(se) # add all of the ScheduleEvents
        
    def recurring_events_gen(self, re: event.RecurringEvent) -> 'generator of event.RecurringEvent':
        '''
        convert a RecurringEvent into a bunch of ScheduleEvents from re.period_start to re.period_end
        if re.period_start is None, use self.region.start as the beginning period
        generate ScheduleEvent.start and ScheduleEvent.end using util.weeklydays()
        :param re: the RecurringEvent to generate from
        '''
        for day in weeklydays(self.region.start if re.period_start is None else re.period_start, re.period_end, re.days):
            # make dates from the RecurringEvent's start_time and end_time
            start_datetime = combine(day, re.start_time)
            # if re is a SleepEvent and the start_time is after the end_time, advance to the next day
            end_datetime = combine(day+datetime.timedelta(day=int(isinstance(re, event.SleepEvent) and re.start_time > re.end_time)), re.start_time)
            # generate a ScheduleEvent
            yield ScheduleEvent(name=re.name, desc=re.desc, start=start_datetime, end=end_datetime, extra_info=re_extra_info)
        

    def task_events_gen(self, te: event.TaskEvent) -> ('generator of event.TaskEvent', Region, 'SortedList of ScheduleEvent'):
        '''
        convert a TaskEvent into a bunch of ScheduleEvents
        :param te: the TaskEvent to generate from
        '''    
        pass # delete this pass after implementing
    
    
    
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
        return (se for se in self.actual_events if start <= se.start and end >= se.end)
        
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
            print(se)
    
