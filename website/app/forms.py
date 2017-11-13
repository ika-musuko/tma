from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length
from .models import User

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])    
    email = StringField('email', validators=[DataRequired()])    
    phone = StringField('phone', validators=[DataRequired()])    
    
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