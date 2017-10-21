import event
import datetime
import sqlite3
from Collections import deque
'''
    schedule.py
    

'''


class ScheduleEvent(event.Event):
    '''
    Schedule will convert every element in its user_events into this type of event
    '''
        def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                ):
        event.Event.__init__(name, desc, priority, start, end)
        
class EventQueue():
    '''
    Priority Queue of ScheduleEvent
    constructor converts a list of event.Event into an EventQueue
    '''
    def __init__(self, events: list=None):
        self.q = deque()
        
       
    def peek() -> ScheduleEvent:
        '''
        peek topmost ScheduleEvent
        '''
    
    def pop() -> ScheduleEvent:
        '''
        remove and return topmost ScheduleEvent
        '''
    
    def push(e: event.Event):
        '''
        convert e into a ScheduleEvent and push with priority
        '''
    
    def push_list(events: list):
        '''
        push a list of event.Event into an EventQueue
        '''
        for e in events:
            self.push(e)
    
class Schedule:

    def __init__(self, events: list=None):
        '''
        create a schedule from a list of Event
        Attributes:
            user_events (list of Event): all the user events
            actual_events (PriorityQueue of ScheduleEvent): every user_event will get converted into this type and get scheduled
        '''
        self.user_events = events
        self.actual_events = self.enqueue_user_events()
        self.update()
    

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
            not None - conflicting Event
        '''
        
    def enqueue_user_events() -> EventQueue:
        '''
        get all of the events from user_events and return an EventQueue for displaying on a schedule
        '''
        return EventQueue(self.user_events)   