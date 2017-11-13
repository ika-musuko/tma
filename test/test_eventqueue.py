import unittest
import sys
import datetime
sys.path.append("../src")
from eventqueue import EventQueue
import event

def event_pusher() -> EventQueue:
    '''
    pushes a default set of events
    '''
    eq = EventQueue()
    event.Event.total = 0
    eq.push(event.TaskEvent(name="Task Event should be below Due"))
    eq.push(event.DueEvent(due=datetime.datetime(2000, 1, 3, 15, 10, 0), name="some Due Event" ))
    for st in range(3, 7):
        eq.push(event.Event(  name="Event %i" % st 
                        , desc="Test"
                        , start=datetime.datetime(2000, 1, 1, st*2, 0)
                        , end=datetime.datetime(2000, 1, 1, st*2+1, 0)
                       ) )
    eq.push(event.SleepEvent( start_time=datetime.time(22, 0, 0)
                             ,end_time=datetime.time(5, 0, 0)))
    eq.push(event.RecurringEvent(name="Recurring Event", start_time=datetime.time(18, 15, 0), end_time=datetime.time(18, 45, 0)))
    return eq

'''
The main idea of these tests is to check if events get properly pushed on the queue. This means that the events should be sorted by the Event's priority field.

methods to test:
    'empty', 
    'peek',  
    'push', 

event types -> default priority:
    'AssignmentEvent',  -> 57
    'DueEvent',         -> 64
    'Event',            -> 0
    'RecurringEvent',   -> 0
    'SleepEvent',       -> 0 
    'TaskEvent'         -> 200

events with a higher value should come later in the queue
'''
class EventQueueTest(unittest.TestCase):


    def test_empty(self):
        eq = EventQueue()
        self.assertEqual(len(eq.q), 0)

    # verify that the topmost item on the queue has the lowest priority value(top priority)
    def test_peek(self):
        eq = event_pusher()
        test_event = eq.peek()
        print(eq)
        for e in eq.q[1:]:
            self.assertLessEqual(test_event.priority, e.priority)
        
    
    # verify that each element on the event queue is pushed in sorted order
    def test_push(self):
        eq = event_pusher()
        for e1, e2 in zip(eq.q, eq.q[1:]):
            self.assertLessEqual(e1.priority, e2.priority)

if __name__ == "__main__":
    unittest.main()
