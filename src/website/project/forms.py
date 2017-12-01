import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField, SelectMultipleField
#from wtforms.fields.html5 import DateField
from wtforms.widgets.html5 import TimeInput
from wtforms_components import TimeField
from wtforms.validators import DataRequired, Length, Optional
from . import CELLPHONE_PROVIDERS
from .models import User
from .scheduler import event, schedule

def if_filled(data, userthing):
    ### helper function for only updating non-blank data
    return userthing if data == "" else data


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


### DATETIME FIELDS ###
# adapted from https://gist.github.com/tachyondecay/6016d32f65a996d0d94f#file-datetimeform-py-L2
from .datetimeform import TimeField
from wtforms.ext.dateutil.fields import DateField, DateTimeField

### EVENT FORMS ###
# for use in adding or editing an event
### the actual event forms
DAYS_OF_THE_WEEK = [('Sun','N'), ('Mon', 'M'), ('Tue', 'T'), ('Wed', 'W'), ('Thu', 'H'), ('Fri', 'F'), ('Sat', 'S')]
EVENT_PRIORITY = [('low', 2), ('normal', 1), ('high', 0)]
TASK_EVENT_PRIORITY = [('low', 189), ('normal', 179), ('high', 169)]
DUE_EVENT_PRIORITY = [('low', 89), ('normal', 79), ('high', 69)]
def list_swapper(seq):
    # sorry : (
    return [(c[1], c[0]) for c in seq]

class EventForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    start = DateTimeField('start')
    end = DateTimeField('end', validators=[Optional()])

class SleepScheduleForm(FlaskForm):
    sleep = TimeField('sleep', validators=[DataRequired()])
    wake = TimeField('wake', validators=[DataRequired()])

class RecurringEventForm(FlaskForm): 
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    days = SelectMultipleField(label='Select Days of the Week', choices=list_swapper(DAYS_OF_THE_WEEK))
    period_start = DateField('period_start', validators=[Optional()])
    period_end = DateField('period_end', validators=[Optional()])
    start_time = TimeField('start_time', validators=[DataRequired()])
    end_time = TimeField('end_time', validators=[DataRequired()])

class TaskEventForm(FlaskForm):
    # for use with task or due events
    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    due = DateTimeField('due', validators=[Optional()]) # optional, for DueEvents
    finished = BooleanField('finished')
    duration = IntegerField('time', validators=[Optional()])

### DELETE EVENT FORM ###
# todo

def isblank(thing):
    return thing == "" or thing is None

### handling form to event conversion
def form_to_event(form: FlaskForm):
    ### method to convert a FlaskForm into an event. yay polymorphism abuse
    form_to_event_dict = {
          EventForm             : event_form_conv
        , SleepScheduleForm     : sleep_form_conv
        , RecurringEventForm    : recurring_form_conv
        , TaskEventForm         : task_form_conv
    }
    return form_to_event_dict[type(form)](form)

def event_form_conv(form: EventForm) -> event.Event:
    if isblank(form.end.data):
        return event.Event(name = form.name.data, desc = form.desc.data, start = form.start.data)
    return event.Event(
                           name  = form.name.data
                         , desc  = form.desc.data
                         , start = form.start.data
                         , end   = form.end.data
                      )

def sleep_form_conv(form: SleepScheduleForm) -> event.SleepEvent:
    return event.SleepEvent(
                                start_time = form.sleep.data
                              , end_time   = form.wake.data
                           )

def recurring_form_conv(form: RecurringEventForm) -> event.RecurringEvent:
    return event.RecurringEvent(
                                      start_time    = form.start_time.data
                                    , end_time      = form.end_time.data
                                    , name          = form.name.data
                                    , desc          = form.desc.data
                                    , period_start  = form.period_start.data
                                    , period_end    = form.period_end.data
                                    , daystr        = ''.join(d for d in form.days.data)
                               )

def task_form_conv(form: TaskEventForm) -> "event.TaskEvent or event.DueEvent":
    if form.due.data == "" or form.due.data is None:
        return event.TaskEvent(
                          name     = form.name.data
                        , desc     = form.desc.data
                        , done     = form.finished.data
                        , duration = form.duration.data
                    ) 
    return event.DueEvent (
                          due      = form.due.data
                        , name     = form.name.data
                        , desc     = form.desc.data
                        , done     = form.finished.data
                        , duration = form.duration.data
                    )
    
