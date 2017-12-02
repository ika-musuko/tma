# create the flask app object
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_heroku import Heroku

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'login required to view'


CELLPHONE_PROVIDERS = {
         '' : ''
        ,'Alltel': 'mms.alltelwireless.com'
        ,'AT&T': 'mms.att.net'
        ,'Boost Mobile' : 'myboostmobile.com'
        ,'Cricket Wireless': 'mms.att.net'
        ,'MetroPCS': 'mymetropcs.com'
        ,'Project Fi': 'msg.fi.google.com'
        ,'Republic Wireless': 'text.republicwireless.com'
        ,'Sprint': 'pm.sprint.com'
        ,'Ting': 'message.ting.com'
        ,'T-Mobile': 'tmomail.net'
        ,'US Cellular': 'mms.uscc.net'
        ,'Verizon Wireless': 'vzwpix.com'
        ,'Virgin Mobile': 'vmpix.com'
}


heroku_deploy = os.environ.get('HEROKU')

if not app.debug and heroku_deploy is None:
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler
    heroku = Heroku(app)
    credentials = None
    # if MAIL_USERNAME or MAIL_PASSWORD:
        # credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    # mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@'+MAIL_SERVER, ADMINS, 'time management fail', credentials)
    # mail_handler.setLevel(logging.ERROR)
    # app.logger.addHandler(mail_handler)
    
    file_handler = RotatingFileHandler('tmp/time_management_error.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('time management')  

if heroku_deploy is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('time management assistant STARTUP!')

from . import views, models
db.create_all()
if __name__ == "__main__":
    manager.run()
