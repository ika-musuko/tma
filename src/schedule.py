import event
import datetime
import sqlite3
import heapq

'''
    schedule.py
'''
        
class EventQueue:
    '''
    Priority Queue of ScheduleEvent
    constructor converts a list of event.Event into an EventQueue
    Attributes:
        q (list of ScheduleEvent): priority queue of ScheduleEvent
        latest_due (event.DueEvent): the latest DueEvent (the DueEvent with the latest due date)
    '''
    def __init__(self                
                    , events: list=[]
                ):
        self.q = []
        self.latest_due = None
        EventQueue.lastpriority = 0
        self.push_list(events)
     
    def delete_by_id(id: int) -> bool:
        '''
        delete event by id
        return value:
            True -> found and deleted
            False -> not found, nothing deleted
        '''
        for i, e in enumerate(self.q):
            if e.id == id:
                self.q.pop(i)
                return False
        else:
            return True
    
    def peek() -> event.Event:
        '''
        peek topmost Event
        '''
        return self.q[0] if len(q) > 0 else None
    
    def pop() -> event.Event:
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
        # don't push a TaskEvent which is already done
        if isinstance(e, TaskEvent) and e.done:
            return
        # if a DueEvent is being pushed, update self.latest_due
        elif isinstance(e, event.DueEvent):
            if self.latest_due is None or e.due > self.latest_due.due:
                self.latest_due = e
        # if pushing an event which is not a DueEvent, make sure DueEvents are above everything except RecurringEvents    
        elif (not isinstance(e, event.RecurringEvent)) and (self.latest_due is not None) and (e.priority < self.latest_due.priority):
            e.priority = self.latest_due.priority + 1           
        heappq.heappush(self.q, e)
        
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
    the start and end boundaries of a Schedule (for viewing)
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

def weeklydays(region: Region, dayofweek: str) -> list:
    '''
    generator of list of days in week from dayofweek in region
    ex:
        weeklydays(r, "T") -> generates every Tuesday in r 
    return value:
        list of datetime.date
    '''
    current_date = region.start
    next_day_increment = ({d: i for i, d in enumerate("MTWHFSN")}[dayofweek] - region.start.weekday()) % 7
    current_date += datetime.timedelta(days=next_day_increment) # go to the next day that matches dayofweek
    while current_date < region.end:
        yield current_date
        d += datetime.timedelta(days=7) # go to next week
    
class Schedule:

    def __init__(self
                    , events: list=[],
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
        self.event_queue = EventQueue(events)
        self.update()
      
    def update(self):
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        self.actual_events = []
        se = []
        for e in self.event_queue:
            extra_info = ""
            # generate corresponding events in region 
            if isinstance(e, event.RecurringEvent):
                
            else:
                se = (ScheduleEvent(e.name, e.desc, e.priority, e.start, e.end, extra_info),)
            # append every generated event to self.actual_events
            self.actual_events.extend(se)
    
    def add_event(e: event.Event):
        '''
        add event
        '''
        self.event_queue.push(e)
    
    def delete_event(id: int) -> bool:
        '''
        delete Event by id
        '''
        self.event_queue.delete_by_id(id)
        