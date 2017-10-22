import event
import datetime
import sqlite3
import heapq

'''
    schedule.py
'''


class ScheduleEvent(event.Event):
    '''
    Schedule will convert every element in its user_events into this type of event
        
    combining a date and time: https://vgy.me/LLwv0g.png
    
    Parent:
        Event
    Attributes:
        extra_info: other information such as due date for DueEvents and recurrence for RecurringEvents
    '''
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                    , extra_info: str=""
                ):
    event.Event.__init__(name, desc, priority, start, end)
    self.extra_info = extra_info
        
class EventQueue:
    '''
    Priority Queue of ScheduleEvent
    constructor converts a list of event.Event into an EventQueue
    Attributes:
        q (list of ScheduleEvent): priority queue of ScheduleEvent
    '''
    def __init__(self                
                    , events: list=[]
                ):
        self.q = []
        self.push_list(events)
       
    def peek() -> ScheduleEvent:
        '''
        peek topmost Event
        '''
        return self.q[0] if len(q) > 0 else None
    
    def pop() -> ScheduleEvent:
        '''
        remove and return topmost Event
        '''
        top = self.peek()
        try:
            heapq.heappop(self.q)
        return top
              
    def push(e: event.Event):
        '''
        push with priority (key is e.priority)
        '''
        heappq.heappush(self.q, (e.priority, e))
        
    def push_list(events: list):
        '''
        push a list of event.Event into an EventQueue
        '''
        for e in events:
            self.push(e)
    
    def empty():
        return self.q is None or len(self.q) <= 0
        
class Region:
    DEFAULT_START = datetime.datetime(2017, 1, 1, 0, 0, 0)
    DEFAULT_END = datetime.datetime(2099, 1, 1, 0, 0, 0)
    '''
    the start and end boundaries of a Schedule
    Attributes:
        start (datetime.datetime): starting datetime
        end (datetime.datetime): ending datetime
    '''
    def __init__(self
                    , start: datetime.datetime=Region.DEFAULT_START
                    , end: datetime.datetime=Region.DEFAULT_END
                ):
        # verify that start is chronologically before end
        if start > end:
            start = Region.DEFAULT_START 
            end = Region.DEFAULT_END
            
        self.start = start
        self.end = end
            
class Schedule:

    def __init__(self
                    , events: list=[],
                    , region: Region=Region()
                ):
        '''
        create a schedule from a list of Event
        Attributes:
            user_events (list of Event): all the user events
            actual_events (list of ScheduleEvent): every user_event will get converted into a ScheduleEvent and scheduled according to the current 
            event_queue (EventQueue): every event
            region (Region): the start and end dates to push actual_events in
        '''
        # initialize arguments
        self.user_events = events
        self.actual_events = []
        self.region = region
        
        self.event_queue = self.enqueue_user_events()
        self.update()
    
    def update(self):
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        
    
    def add_event(e: event.Event) -> bool:
        '''
        checks for conflicts and then adds an Event to the Schedule
        return value:
            True - successful addition
            False - unsuccessful, no addition
        '''
        if self.check_conflict() == None:
            self.user_events.append(e)
            return True
        ## future: show conflicting event?
        return False
        
    def check_conflict(e: event.Event) -> event.Event:
        '''
        check if e conflicts with another event.Event in user_events
        return value:
            None - no conflict
            not None - the conflicting Event
        '''
        
    def enqueue_user_events() -> EventQueue:
        '''
        get all of the events from user_events and return an EventQueue for displaying on a schedule
        '''
        return EventQueue(self.user_events)   