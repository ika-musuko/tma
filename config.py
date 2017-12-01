'''
config.py
configuration file for flask
'''

### SQLALCHEMY CONFIG ###
import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

### GOOGLE CONFIG ###
# dynamically load google authorization from file


#with open("gconf.keys", "r") as gconf:
#    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET = gconf.read().splitlines()

# no local file storage on heroku : ( hardcoded lol pls don't look


GOOGLE_CLIENT_ID = "302888478518-1306kq0h1cv540fma6tqc3pafk9bhbdh.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "Jq3Kmr8by4CifX_xVhK6O6fn"

#print("GOOGLE CRAP %s\n%s" % (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))

### OAUTH CONFIG ###
# canvas would be included here as well when that is implemented
OAUTH_CREDENTIALS = {
    'google' : {
         'id' : str(GOOGLE_CLIENT_ID)
        ,'secret' : str(GOOGLE_CLIENT_SECRET)
    }
}

### WTFORMS CONFIG ###
WTF_CSRF_ENABLED = True


### what is this ###
SECRET_KEY = "iguessineedthis..."
