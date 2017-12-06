import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, SelectMultipleField, widgets
#from wtforms.fields.html5 import DateField
from wtforms.widgets.html5 import TimeInput
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, Length, Optional
from . import CELLPHONE_PROVIDERS
from .models import User, UserScheduleEvent, UserEvent
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
    #reminder_frequency = IntegerField('Reminder frequency (in days) (0 for off)', validators=[Optional()])

    '''
    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname
        
    '''
    def validate(self):
        return True

### MULTICHECKBOX FIELD ###        
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()
        
### EVENT FORMS ###
# for use in adding or editing an event

DAYS_OF_THE_WEEK = [('Sun','N'), ('Mon', 'M'), ('Tue', 'T'), ('Wed', 'W'), ('Thu', 'H'), ('Fri', 'F'), ('Sat', 'S')]
EVENT_PRIORITY = [('low', 2), ('normal', 1), ('high', 0)]
TASK_EVENT_PRIORITY = [('low', 189), ('normal', 179), ('high', 169)]
DUE_EVENT_PRIORITY = [('low', 89), ('normal', 79), ('high', 69)]
def list_swapper(seq):
    # sorry : (
    return [(c[1], c[0]) for c in seq]

def edit_form_with_args(e: UserEvent):       
    if e.type == "RecurringEvent": 
        return RecurringEventForm(
                name          =e.name   
               ,desc          =e.desc   
                
               ,period_start  =e.recEvent_period_start
               ,period_end    =e.recEvent_period_end  
               ,start_time    =e.recEvent_start_time  
               ,end_time      =e.recEvent_end_time    
               ,days          =e.recEvent_daystr      
               )
   
    elif e.type == "SleepEvent":        
        return SleepScheduleForm(
                     sleep    =e.recEvent_start_time
                    ,wake     =e.recEvent_end_time
                    )
                    
    elif e.type == "TaskEvent":         
        return TaskEventForm(
                     name     =e.name
                    ,desc     =e.desc
                    ,duration =e.taskEvent_duration
                    ,done     =e.taskEvent_done
                    )
    elif e.type == "DueEvent":          
        return TaskEventForm(
                     name     =e.name
                    ,desc     =e.desc
                    ,due      =e.dueEvent_due
                    ,duration =e.taskEvent_duration
                    ,done     =e.taskEvent_done
                    )
                    
    return EventForm(
                     name     =e.name
                    ,desc     =e.desc
                    ,start    =e.start
                    ,end      =e.end
                    )
        



## the actual event forms    
class EventForm(FlaskForm):
    name  = StringField('Name', validators=[DataRequired()])
    desc  = TextAreaField('Description')
    start = DateTimeField('Start Date/Time')
    end   = DateTimeField('End Date/Time', validators=[Optional()])

class SleepScheduleForm(FlaskForm):
    sleep = TimeField('Sleep Time', validators=[DataRequired()])
    wake = TimeField('Wake Time', validators=[DataRequired()])

class RecurringEventForm(FlaskForm): 
    name         = StringField('Name', validators=[DataRequired()])
    desc         = TextAreaField('Description')
    days = MultiCheckboxField(label='Select Days of the Week', choices=list_swapper(DAYS_OF_THE_WEEK))
    period_start = DateField('Generate From Date', validators=[Optional()])
    period_end   = DateField('Generate To Date', validators=[Optional()])
    start_time   = TimeField('Start Time', validators=[DataRequired()])
    end_time     = TimeField('End Time', validators=[DataRequired()])

class TaskEventForm(FlaskForm):
    # for use with task or due events
    name = StringField('Name', validators=[DataRequired()])
    desc = TextAreaField('Description')
    due = DateTimeField('Due Date/Time', validators=[Optional()]) # optional, for DueEvents
    duration = IntegerField('Time', validators=[Optional()])
    finished = BooleanField('finished')

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
                        , duration = form.duration.data
                        , done = form.finished.data
                    ) 
    return event.DueEvent (
                          due      = form.due.data
                        , name     = form.name.data
                        , desc     = form.desc.data
                        , duration = form.duration.data
                        , done = form.finished.data
                    )
 
# dynamic type abuse 
formdict = {
        'regular'   : EventForm 
       ,'sleep'     : SleepScheduleForm  
       ,'recurring' : RecurringEventForm
       ,'task'      : TaskEventForm
       
       ,event.Event           : EventForm 
       ,event.SleepEvent      : SleepScheduleForm 
       ,event.RecurringEvent  : RecurringEventForm
       ,event.TaskEvent       : TaskEventForm
       ,event.DueEvent        : TaskEventForm
}
