from sortedcontainers import SortedList
from app.scheduler import event

class EventQueue:
    '''
    Priority Queue of Event
    constructor converts a list of event.Event into an EventQueue
    Attributes:
        q (list of ScheduleEvent): priority queue of ScheduleEvent
        latest_due (event.DueEvent): the latest DueEvent (the DueEvent with the latest due date)
    '''
    def __init__(self                
                    , events: list=None
                ):
        self.q = SortedList()
        self.latest_due = None
        EventQueue.lastpriority = 0
        if events is None:
            events = []
        self.push_list(events)
     
    def __iter__(self):
        return iter(self.q)
    
    def __getattr__(self, index):
        return self.q[index]

    def delete_by_id(self, id: int) -> bool:
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
    
    def peek(self) -> event.Event:
        '''
        peek topmost Event
        '''
        return self.q[0] if len(self.q) > 0 else None
    
    def pop(self) -> event.Event:
        '''
        remove and return topmost Event
        '''
        top = self.peek()
        if(len(self.q) > 0):
            self.q.pop(0)
        return top
              
    def push(self, e: event.Event):
        '''
        push with priority (key is e.priority)
        '''
        # don't push a TaskEvent which is already done
        if isinstance(e, event.TaskEvent) and e.done:
            return
        # if a DueEvent is being pushed, update self.latest_due
        #elif isinstance(e, event.DueEvent):
        #    if self.latest_due is None or e.due > self.latest_due.due:
        #        self.latest_due = e
        # if pushing an event which is not a DueEvent, make sure DueEvents are above everything except RecurringEvents    
        #elif (not isinstance(e, event.RecurringEvent)) and (self.latest_due is not None) and (e.priority < self.latest_due.priority):
        #   e.priority = self.latest_due.priority + 1 
        #   pass
        self.q.add(e)
        
    def push_list(self, events: list):
        '''
        push a list of event.Event into an EventQueue
        '''
        for e in events:
            self.push(e)
    
    def empty(self):
        return self.q is None or len(self.q) <= 0
        
    def __repr__(self):
        return ''.join(("~~ EventQueue ~~\n", '\n'.join(str(qe) for qe in self.q)))
