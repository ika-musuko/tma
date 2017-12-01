# https://gist.github.com/tachyondecay/6016d32f65a996d0d94f#file-datetimeform-py-L2
import datetime

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.widgets.html5 import TimeInput

class TimeField(StringField):
    """HTML5 time input."""
    widget = TimeInput()

    def __init__(self, label=None, validators=None, format='%H:%M:%S', **kwargs):
        super(TimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                components = time_str.split(':')
                hour = 0
                minutes = 0
                seconds = 0
                if len(components) in range(2,4):
                    hour = int(components[0])
                    minutes = int(components[1])

                    if len(components) == 3:
                        seconds = int(components[2])
                else:
                    raise ValueError
                self.data = datetime.time(hour, minutes, seconds)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time string'))


class DateTimeForm(FlaskForm):
    """
    Replaces the default wtforms `DateTimeField` with one that combines the 
    HTML5 `date` and `time` inputs.
    """
    
    date_field = DateField()
    time_field = TimeField()
    
    def __init__(self, name, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.name = name
        self.field_type = self.__name__

    # Use this property to get/set the values of the date and time fields 
    # using a single datetime from an object, e.g., in a form's `__init__` method.
    @property
    def datetime(self):
        if self.date_field.data and self.time_field.data:
            return datetime.datetime.combine(self.date_field.data, self.time_field.data)

    @datetime.setter
    def datetime(self, value):
        self.date_field.data = value.date()
        self.time_field.data = value.time()
