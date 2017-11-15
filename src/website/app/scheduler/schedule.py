from . import event
from .eventqueue import EventQueue
import datetime
import sqlite3
from sortedcontainers import SortedList
import operator
import math
from . import txt
from .util import *
from . import canvas

'''
    schedule.py

    the main scheduling system and automatic schedule generator
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
        {desc}
        {dow}
        start: {start}
        end: {end}
        {ei}
        '''.format(name=self.name, desc=self.desc, dow=ScheduleEvent.DAY_NAMES[self.start.weekday()], start=hm(self.start), end=hm(self.end), ei=self.extra_info)
    
    def __repr__(self):
        return ": ".join(("ScheduleEvent", str(self.__dict__)))

    def short_print(self):
        today = datetime.datetime.now()
        dow = "Today" if self.start.weekday() == today.weekday() else "Tomorrow" if (self.start.weekday() - today.weekday())%7 == 1 else ScheduleEvent.DAY_NAMES[self.start.weekday()]
        return "{name}\n{dow}\nstart: {start}\nend: {end}\n".format(name=self.name, dow=dow, start=hm(self.start), end=hm(self.end))

class Schedule:
    '''
    Schedule constructor
    create a schedule from a list of Event
    Attributes:
    actual_events (list of ScheduleEvent): every user_event will get converted into a ScheduleEvent and scheduled according to the current 
    param event_queue (EventQueue): every event
    param region (Region): the start and end dates to push actual_events in
    '''
    zerotime = datetime.time()
    def __init__(self
                    , events: list=[]
                    , start: datetime.datetime=None
                    , end: datetime.datetime=None
                    , desired_courses: list=None
                ):
        # initialize arguments
        self.actual_events = []
        self.desired_courses = desired_courses
        self.region = Region(start, end)
        self.region.fill()
        self.work_time = 90 # how long doing one stretch of work is in minutes
        self.break_time = 15 # how long a break is in minutes
        self.event_queue = EventQueue(events)
        self.current_event = None
        self.update()

    @property
    def event_data(self):
        return self.event_queue

    @property
    def calendar_event_data(self):
        return self.actual_events

    def update(self) -> None:
        '''
        pop ScheduleEvents off of self.event_queue and push them into self.actual_events, assigning ScheduleEvent.start and ScheduleEvent.end to events that have none
        '''
        # if the current region.start is earlier than today, make the earliest free region's start earlier than today. else, maintain the current region.start for earliest free region
        self.today = datetime.datetime.today()
        self.earliest_free_region = Region(self.today if self.region.start < self.today else self.region.start, self.region.end)
        self.found_current_event = False
        self.generated_events = SortedList()
        self.actual_events = SortedList()

        # go through all of the events on the queue...
        print("~~~ PROCESSING EVENT QUEUE ~~~")
        for e in self.event_queue:
            print(e)
            # se is an iterable of ScheduleEvent
            if isinstance(e, event.RecurringEvent):
                se = self.generate_recurring_events(e)
            elif isinstance(e, event.TaskEvent):
                se = self.generate_task_events(e)
            # this is just a normal event so turn it into a tuple of 1 element to extend
            else:
                se = (ScheduleEvent(name=e.name, desc=e.desc, start=e.start, end=e.end, extra_info="USER EVENT"),)
            self.push_generated_events(se, self.today)
            sort_extend(self.actual_events, se) # add all of the ScheduleEvents

        # get the current event
        if self.current_event is None:
            for ae in self.actual_events:
                if ae.start <= self.today <= ae.end:
                    self.current_event = ae
                    break

        print("~~~PROCESSING FINISHED ~~~")
    
    ### AUTOMATIC SCHEDULE GENERATING ALGORITHM
    def push_generated_events(self, se: list, today: datetime.datetime) -> None:
        '''
        push generated events only if they happened after today
        :param se: the list of events to push
        :param today: what is today???
        '''
        sort_extend(self.generated_events, [s for s in se if s.start >= today])
    
    def generate_recurring_events(self, re: event.RecurringEvent) -> 'SortedList of ScheduleEvent':
        '''
        convert a RecurringEvent into a bunch of ScheduleEvents from re.period_start to re.period_end
        if re.period_start is None, use self.region.start as the beginning period
        generate ScheduleEvent.start and ScheduleEvent.end using util.weeklydays()
        :param re: the RecurringEvent to generate from
        :return value: the generated ScheduleEvents
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
                
                # if self.earliest_free_region is inside an event happening right now, move it and make it the current event
                if not self.current_event is None and new_se.start <= self.today < new_se.end:
                    self.earliest_free_region.start = new_se.end
                    self.current_event = new_se

                se.add(new_se)
        return se

    def generate_task_events(self, te: event.TaskEvent) -> 'SortedList of ScheduleEvent':
        '''
        convert a TaskEvent into a bunch of ScheduleEvents by fixing conflicts between events by checking if the start and end datetimes are inside another existing event or if they engulf another event, and readjusting the start and end times to match the boundaries of the conflicting events
        :param te: the TaskEvent to generate from
        :return value: the generated ScheduleEvents
        '''    
        print("\tconverting & generating: %r" % te)
        remaining_duration = te.duration
        se = SortedList()
        allocate_break = False
        # break up into multiple events until the event's entire duration has passed
        while remaining_duration > 0 : 
            # allocate a break if the remaining duration is longer than the user's desired work time
            allocate_break = remaining_duration > self.work_time
            # assign start and end datetime for event
            start_datetime, end_datetime = self.set_event_times(self.work_time if allocate_break else remaining_duration)

            # get the current remaining duration
            event_length = tominutes(end_datetime - start_datetime)
            remaining_duration -= event_length
            self.earliest_free_region = Region(end_datetime, self.region.end) # set the free region to after the new event was created
            if(event_length > 0): # hack fix for ignoring "microevents" (less than one minute)
                # create the new event
                te_extra_info = "DUE EVENT: due: %s" % (te.due) if isinstance(te, event.DueEvent) else "Task Event"
                new_se = ScheduleEvent(name=te.name, desc=te.desc, start=start_datetime, end=end_datetime, extra_info=te_extra_info)
                se.add(new_se)
                print("\t\tstart: %s end: %s" %(new_se.start, new_se.end))

                # set a break event
                if allocate_break:
                    start_break, end_break = self.set_event_times(self.break_time)
                    if start_break == new_se.end: # don't allocate unnecessary breaks after other events
                        new_break = ScheduleEvent(name="Break", desc="", start=start_break, end=end_break, extra_info="generated break event")
                        se.add(new_break)
                        self.earliest_free_region = Region(new_break.end, self.region.end)
                        print("\t\tgenerated break: start %s end %s" % (new_break.start, new_break.end))
        return se
    
    def set_event_times(self, duration: int) -> '(start=datetime.datetime, end=datetime.datetime)':
        '''
        helper method for setting event start and end datetimes
        :param duration: duration in minutes
        '''
        # set the start time 
        start_datetime = self.earliest_free_region.start # use the start of the earliest_free_region
        conflict = self.check_start(start_datetime)
        if conflict is not None:
            start_datetime = conflict.end
        
        # set the end time
        end_datetime = start_datetime + datetime.timedelta(minutes=duration)
        conflict = self.check_end(start_datetime, end_datetime)
        if conflict is not None:
            end_datetime = conflict.start

        return (start_datetime, end_datetime)

    def check_start(self, dt: datetime.datetime) -> ScheduleEvent:
        '''
        check if a datetime.datetime is inside any generated events
        :param dt: the datetime to check
        :return value: the conflicting event or None if there are no conflicting events
        '''
        for ge in self.generated_events:
            if ge.start > dt:
                    return None # return early if we have gone past the dt since self.generate_events is sorted
            if ge.start <= dt < ge.end:
                    return ge
        return None
    
    def check_end(self, start: datetime.datetime, end: datetime.datetime) -> ScheduleEvent:
        '''
        check if a datetime.datetime is inside any generated events and start and end are not encapsulating any event
        :param start: the start datetime to check
        :param end: the end datetime to check
        :return value: the conflicting event or None if there are no conflicting events
        '''
        for ge in self.generated_events:
            if ge.start > end:
                    return None # return early if we have gone past the dt since self.generate_events is sorted
            if ge.start <= end <= ge.end or (ge.start >= start and ge.end <= end):
                    return ge
        return None        
        
    def add_event(self, e: event.Event) -> None:
        '''
        add event
        :param e: the Event to add
        '''
        self.event_queue.push(e)
        self.update()

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
    
    def add_canvas_assignments(self, login: str) -> bool:
        '''
        adds assignments from canvas into Schedule
        :param login: the canvas api_key (todo, use real authentication with a user and password)
        :return value: whether it was successful or not
        '''
        try:
            self.event_queue.push_list(canvas.get_assignments(login))
            self.update()
            return True
        except:
            return False
    
    def add_canvas_calendar(self, login: str) -> bool:
        '''
        adds canvas calendar events into schedule as normal events
        :param login: the canvas api_key (todo, use real authentication with a suer and password)
        :return value: whether it was successful or not
        '''
        try:
            self.event_queue.push_list(canvas.get_calendar_events(login))
            self.update()
            return True
        except:
            return False
    
    
    def desired_course_check(e: event.Event) -> bool:
        '''
        checks if an AssignmentEvent is in the desired classes
        '''
        return (self.desired_course is None) or (not isinstance(e, event.AssignmentEvent)) or (e.course_id in self.desired_course)
    
    def get_courses(self, login: str) -> bool:
        '''
        get course list from canvas and store to Schedule
        :param login: the canvas api_key (todo, use real authentication with a user and password)
        :return value: whether it was successful or not
        '''
        try:
            self.canvas_courses = canvas.get_courses(login)
            return True
        except HTTPError as e:
            print(e)
            self.canvas_courses = None
            return False

    def delete_event(self, id: int) -> bool:
        '''
        delete Event by id
        :param id: look for the event with this id to delete
        :return value: if the delete was successful
        todo - after the UI is properly conceptualized, these params might have to be changed?
        '''
        self.event_queue.delete_by_id(id)
    
    def get_events_in_region(self, start: datetime.datetime, end: datetime.datetime) -> 'generator of ScheduleEvent':
        '''
        return a generator of every actual event from start to end
        :param start: start generator from here
        :param end: end generator here
        :return value: the events in the region
        '''
        if start is None:
            start = self.region.start
        if end is None:
            end = self.region.end    
        return (se for se in self.actual_events if start <= se.start <= end)
    
    def send_message(self, address: str, start: datetime.datetime=None, end: datetime.datetime=None):
        '''
        sends an email or text message (via multimedia message) of the schedule in a more abbreviated way
        '''
        getactual = self.get_events_in_region(start, end)
        event_list = [se.short_print() for se in getactual]
        message = "Schedule:\n\n"+'\n'.join(event_list)
        txt.send_email(message, address)

    def print_schedule(self
                            , start: datetime.datetime=None
                            , end: datetime.datetime=None
                       ) -> None:
        '''
        print out the schedule to the terminal from start to end
        :param start: start printing from here
        :param end: end printing here
        '''
        getactual = self.get_events_in_region(start, end)
        
        print("-------------------------")
        print("schedule:")
        print("--------------")
        print("CURRENT EVENT:")
        if self.current_event is None:
            print("Nothing going on right now!")
        else:
            print(str(self.current_event)) 
        print("--------------")
        print("upcoming events: ")
        print("--------------")
        for se in getactual:
            print(str(se))
