import datetime
import sqlite3
'''
    event.py
    
    definitions for every type of event
'''

class Event:
    '''
    base class for all events
    examples:
        user assigned events, other custom events
        
    Attributes:
        name (str): name of event
        desc (str): description of event
        priority (int): 0 = highest priority, higher values -> lower priority (ex: 3 has higher priority than 20)
        start (datetime.datetime): start datetime for event
        end (datetime.datetime): end datetime for event
    '''
    total = 0
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                ):
        # set a unique ID for this Event based on how many events have been created        
        self.id = Event.total 
        Event.total += 1
        # initialize class members
        self.priority = priority
        self.start = start
        self.end = end

class TaskEvent(Event):
    '''
    Event with a "done" flag
    the Scheduler will generate TaskEvents until self.done has been set to True
    '''
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , done: bool=False
                ):
        Event.__init__(self, name, desc, priority, None, None)
        self.done = done
    
class DueEvent(TaskEvent):
    '''
    TaskEvent with a due time
    Schedule will generate Events until this event's due date has passed or self.done has been set to True 
    
    examples: 
        homework, projects
    Parent: 
        Event
    Attributes:
        due (datetime.datetime): the due date and time for this event
    '''
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , priority: int=1
                    , done: bool=False
                    , due: datetime.datetime
                ):
       TaskEvent.__init__(self, name, desc, priority, done)
       self.due = due

class RecurringEvent(Event):
    '''
    Event which recurs from period_start to period_end
    if a Schedule sees a RecurringEvent, it will generate more RecurringEvents from period_start to period_end
    if self.period_start is None, this Event will be scheduled from the beginning of time
    if self.period_end is None, this Event will be scheduled to the end of time
    self.priority will be set to 0 because these events will unconditionally be scheduled
    
    the daystr parameter will specify which days of the week this event will be scheduled. 
        legend:
            N - sunday
            M - monday
            T - tuesday
            W - wednesday
            H - thursday
            F - friday
            S - saturday
        example: "THF" -> schedule this event on tuesday, thursday, and friday

    examples:
        classes, work
    Parent:
        Event
    Attributes:
        period_start (datetime.datetime): when to start generating events 
        period_end  (datetime.datetime): when to stop generating events
        start_time (datetime.time): starting time of Event
        end_time (datetime.time): end time of Event   
        
    '''
    fulldays = {
                "N" : "Sunday",
                "M" : "Monday",
                "T" : "Tuesday",
                "W" : "Wednesday",
                "H" : "Thursday",
                "F" : "Friday",
                "S" : "Saturday"
               }
    def __init__(self
                    , name: str=""
                    , desc: str=""
                    , start_time: datetime.time
                    , end_time: datetime.time
                    , period_start: datetime.datetime=None
                    , period_end: datetime.datetime=None
                    , daystr: str=""
                ):
        Event.__init__(self, name, desc, priority=0, start=None, end=None)
        self.period_start = period_start
        self.period_end = period_end
        self.start_time = start_time
        self.end_time = end_time
        
        # initialize recurrence days
        self.days = {d: v for d, v in zip("NMTWHFS", [False]*7)}
        self.whatdays = ""
        for d in daystr:
            self.days[d] = True
            self.whatdays = " ".join(self.whatdays, RecurringEvent.fulldays[d])
    