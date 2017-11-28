from .scheduler import event, schedule
import datetime

from . import db
from flask_login import UserMixin

def init_db():
    db.create_all()

TEST_EVENT = schedule.ScheduleEvent(start=datetime.datetime.today(), end=datetime.datetime.today()+datetime.timedelta(hours=2), name="test event", desc="description lol", extra_info="extra info!", parent_id=1)
TEST_EVENT_2 = schedule.ScheduleEvent(start=datetime.datetime.today()+datetime.timedelta(hours=2), end=datetime.datetime.today()+datetime.timedelta(hours=5), name="test event 2", desc="description lol", extra_info="moar extra infoz", parent_id=2)
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True, unique=True)
    nickname = db.Column(db.String(64), nullable=True, index=True, unique=False)
    email    = db.Column(db.String(256), nullable=False, unique=True)
    phone    = db.Column(db.String(256), nullable=True,index=True, unique=False)
    cellphone_provider = db.Column(db.String(256), nullable=True, index=True, unique=False)
    events  = db.relationship('UserEvent', backref='author', lazy='dynamic')
    scheduleevents = db.relationship('UserScheduleEvent', backref='author', lazy='dynamic')
    
    # figure out how to store canvas info???
    
    ### methods to handle schedule/event stuff ###
        
    def get_events(self):
        return [TEST_EVENT, TEST_EVENT_2]

    ### user property methods ###
    # return True unless there is some reason the user should not be authenticated
    @property
    def is_authenticated(self):
        return True
     
    # return True unless they are inactive (banned, etc)
    @property
    def is_active(self):
        return True
      
    # return False unless this is a fake user
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)
    
    # make sure self.nickname is unique
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname
    
    
    
    def __repr__(self):
        return "<User: %r>" % self.email
 
class UserScheduleEvent(db.Model):
    __tablename__ = 'scheduleevents'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(128), nullable=True, index=True, unique=False)
    desc = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    extra_info = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
 
class UserEvent(db.Model):
    '''
        these are database representations of events that go on the event queue
        these get converted into schedule events by the algorithm
    '''
    __tablename__ = 'events'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=True, index=True, unique=False) # Event, RecurringEvent, TaskEvent, etc
    
    name    = db.Column(db.String(128), nullable=True, index=True, unique=False)
    desc    = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    priority = db.Column(db.Integer, nullable=True, index=True, unique=False)
    start   = db.Column(db.DateTime)
    end     = db.Column(db.DateTime)
    
    taskEvent_done      = db.Column(db.Boolean)
    taskEvent_duration = db.Column(db.Integer)
    
    dueEvent_due = db.Column(db.DateTime)
    
    assignmentEvent_courseid = db.Column(db.String(64), nullable=True, unique=False)
    assignmentEvent_coursename = db.Column(db.String(64), nullable=True, unique=False)
    
    recEvent_period_start = db.Column(db.DateTime)
    recEvent_period_end = db.Column(db.DateTime)
    recEvent_start_time = db.Column(db.Time)
    recEvent_end_time = db.Column(db.Time)
    recEvent_daystr = db.Column(db.String(64), nullable=True, unique=False)
    
    def __repr__(self):
        return "<UserEvent: %r>" % self.name
        



def to_event(de):
    return {
                 "Event"          : to_normal_event
                ,"RecurringEvent" : to_recurring_event
                ,"SleepEvent"     : to_recurring_event
                ,"TaskEvent"      : to_task_event
                ,"DueEvent"       : to_due_event
           }[de.type](de)

def to_normal_event(de):
    return event.Event(  
                             name=de.name
                            ,desc=de.desc
                            ,priority=de.priority
                            ,start=de.start
                            ,end=de.end
                      )

def to_recurring_event(de):
    return event.RecurringEvent(  
                                     name=de.name
                                    ,desc=de.desc
                                    ,priority=de.priority
                                    ,start_time=de.recEvent_start_time
                                    ,end_time=de.recEvent_end_time
                                    ,period_start=de.recEvent_period_start
                                    ,period_end=de.recEvent_period_end
                                    ,daystr=de.recEvent_daystr
                                )

def to_task_event(de):
    return event.TaskEvent(
                              name=     de.name    
                            , desc=     de.desc    
                            , priority= de.priority
                            , done=     de.taskEvent_done    
                            , duration= de.taskEvent_duration
                           )



def to_due_event(de):
    return event.DueEvent(
                             name=     de.name    
                           , desc=     de.desc    
                           , priority= de.priority
                           , done=     de.taskEvent_done    
                           , duration= de.taskEvent_duration
                           , due=      de.dueEvent_due 
                          )                       
                          
if __name__ == "__main__":
    init_db()
