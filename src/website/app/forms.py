from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, DateTimeField, DateField, TimeField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from . import CELLPHONE_PROVIDERS
from .models import User


### SETTINGS FORM ###
class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])    
    email = StringField('email', validators=[DataRequired()])    
    phone = StringField('phone', validators=[DataRequired()])    
    cellphone_provider = SelectField(label="Choose a provider", choices=[(k, k) for k in sorted(CELLPHONE_PROVIDERS.keys())])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname
        
    def validate(self):
        return True
        # if not FlaskForm.validate(self):
            # return False
        # if self.nickname.data == self.original_nickname:
            # return True
        # user = User.query.filter_by(nickname=self.nickname.data).first()
        # print("NAME CHANGE DATA:::: %s" % user)
        # if user is not None:
            # self.nickname.errors.append("this nickname already exists! change it...")
            # return False
        # return True


### EVENT FORMS ###
# for use in adding or editing an event
PRIORITY = [('low','low'), ('normal', 'normal'), ('high', 'high')]
DAYS_OF_THE_WEEK = [('Sun','N'), ('Mon', 'M'), ('Tue', 'T'), ('Wed', 'W'), ('Thu', 'H'), ('Fri', 'F'), ('Sat', 'S')]

class EventForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    start = DateTimeField('start', validators=[DataRequired()])
    end = DatetimeField('end')

class SleepScheduleForm(FlaskForm):
    sleep = TimeField('sleep', validators=[DataRequired()])
    wake = TimeField('wake', validators=[DataRequired()])

class RecurringEventForm(FlaskForm): 
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    days = SelectMultipleField(label='Select Days of the Week', choices=DAYS_OF_THE_WEEK)
    period_start = DateField('period_start')
    period_end = DateField('period_end')
    start_time = TimeField('start_time', validators=[DataRequired()])
    end_time = TimeField('end_time', validators=[DataRequired()])

class TaskEventForm(FlaskForm):
    # for use with task or due events
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    due = DatetimeField('due') # optional, for DueEvents
    finished = BooleanField('finished')

### DELETE EVENT FORM ###
# todo
