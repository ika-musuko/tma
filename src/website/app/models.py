import sys
sys.path.append("../../src")
from src import event, schedule

from app import db, login_manager
from flask_login import LoginManager, UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False, index=True, unique=False)
    email = db.Column(db.String(256), nullable=True,index=True, unique=False)
    phone = db.Column(db.String(256), nullable=True,index=True, unique=False)
    schedule = db.relationship('UserSchedule', uselist=False, back_populates='users')
    # figure out how to store canvas info???
    
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
        return "<User: %r>" % self.nickname

        
class UserSchedule(db.Model):
    __tablename__ = 'schedules'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    id = db.Column(db.Integer, primary_key=True)
    events = db.relationship('UserEvent', backref='user', lazy='dynamic', primaryjoin='UserSchedule.id == UserEvent.id')
    calendarevents = db.relationship('UserCalendarEvent', backref='user', lazy='dynamic', primaryjoin='UserSchedule.id == UserCalendarEvent.id')
    
    def __init__(self, schedule:schedule.Schedule):
        # init this with Schedule data from src
        pass
        
    def __repr__(self):
        return "<UserSchedule: %r>" % self.user_id
 
class UserCalendarEvent(db.Model):
    '''
        these events get written to the calendar
    '''
    __tablename__ = 'calendarevents'
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id')) 
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(128), nullable=True, index=True, unique=False)
    desc = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    extra_info = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    priority = db.Column(db.Integer, nullable=True, index=True, unique=False)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    
    def __init__(self, se: schedule.ScheduleEvent):
        '''
        convert an schedule.ScheduleEvent into a calendar event
        '''
        pass
        
    def __repr__(self):
        return "<ScheduleEvent: %r>" % self.name
 
class UserEvent(db.Model):
    '''
        these are database representations of events that go on the event queue
        these get converted into schedule events by the algorithm
    '''
    __tablename__ = 'events'
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=True, index=True, unique=False) # Event, RecurringEvent, TaskEvent, etc
    
    name = db.Column(db.String(128), nullable=True, index=True, unique=False)
    desc = db.Column(db.String(1024), nullable=True, index=True, unique=False)
    priority = db.Column(db.Integer, nullable=True, index=True, unique=False)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    
    taskEvent_done = db.Column(db.Boolean)
    taskEvent_duration = db.Column(db.Integer)
    
    dueEvent_due = db.Column(db.DateTime)
    
    assignmentEvent_courseid = db.Column(db.String(64), nullable=True, unique=False)
    assignmentEvent_coursename = db.Column(db.String(64), nullable=True, unique=False)
    
    recEvent_period_start = db.Column(db.DateTime)
    recEvent_period_end = db.Column(db.DateTime)
    recEvent_start_time = db.Column(db.Time)
    recEvent_end_time = db.Column(db.Time)
    recEvent_daystr = db.Column(db.String(64), nullable=True, unique=False)
    
    def __init__(self, e: event.Event):
        '''
        convert an event.Event into a database entry
        '''
        pass
    
    def __repr__(self):
        return "<UserEvent: %r>" % self.name