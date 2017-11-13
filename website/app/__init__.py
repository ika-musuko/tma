# create the flask app object

from flask import Flask
from flask sql_alchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config.from_object('config')
database = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import views, models

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@'+MAIL_SERVER, ADMINS, 'time management fail', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    
    file_handler = RotatingFileHandler('tmp/time_management_error.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('time management')  