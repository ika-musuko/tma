from flask import render_template, flash, redirect, url_for, session, make_response, request
from . import app, db, login_manager
from flask_login import login_user, logout_user, current_user, login_required
from .auth import OAuthSignIn
from .forms import form_to_event, EditForm, EventForm, SleepScheduleForm, RecurringEventForm, TaskEventForm, if_filled
from .models import init_db, User, UserSchedule, UserEvent


### HOME PAGE ###
@app.route('/')
@app.route('/index')
def index():
    # todo: get the user's current events and display them here
    if current_user.is_authenticated: 
        return render_template('index.html', todolist=current_user.get_events())
    else:
        return render_template('index.html')

### LOGIN PAGES ###
# standard google login
@app.route('/login')
def login():
    return oauth_authorize('google')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))
    
# canvas login associated with user profile
# todo...

# oauth stuff
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()    


def oauth_callback_base(provider):
    '''
    base function for performing oauth callbacks
    '''
    # perform an oauth request
    oauth = OAuthSignIn.get_provider(provider)
    callback_crap = oauth.callback()
    return callback_crap

@app.route('/callback/google')
def oauth_callback_google():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    callback_crap = oauth_callback_base("google")
    print("google callback: %s" % str(callback_crap))
    _, email = callback_crap
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    # get the user info
    nickname = email.split("@")[0]
    print("user config: nickname: %s email: %s" % (nickname, email))
    user = User.query.filter_by(email=email).first()
    print("user existence: %s" % str(user))
    # if it's a new user, create it
    if user is None:
        
        user = User(nickname=nickname, email=email)
        user.init_schedule()
        db.session.add(user)
        db.session.commit()
    # login the user
    login_user(user, True)
    # go back to the home page
    return redirect(url_for('index'))
    
# todo: write a callback method for canvas...
    
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
    
### EDIT PROFILE PAGE ###
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(current_user.nickname)
    if form.validate_on_submit():
        current_user.nickname           = if_filled(form.nickname.data, current_user.nickname)
        current_user.email              = if_filled(form.email.data, current_user.email)
        current_user.phone              = if_filled(''.join(c for c in form.phone.data if c.isdigit()), current_user.phone)
        current_user.cellphone_provider = if_filled(form.cellphone_provider.data, current_user.cellphone_provider)
        db.session.add(current_user)
        db.session.commit()
        flash("Your settings have been updated.")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = current_user.nickname
    return render_template('edit.html', form=form)

### ADD EVENT PAGE ###
# selector
@app.route('/add_selector')
@login_required
def add_selector():
    return render_template("add_selector.html")

# event adder
@app.route("/add_event/<event_type>", methods=["GET", "POST"])
@login_required
def add_event(event_type):
    formdict = {
            'regular'     : EventForm 
           ,'sleep'     : SleepScheduleForm  # sleep should redirect to editing the sleep schedule but for now it is left here
           ,'recurring' : RecurringEventForm
           ,'task'      : TaskEventForm
    }
    form = formdict[event_type]()
    if form.validate_on_submit():
        formed_event = form_to_event(form)
        current_user.add_event(formed_event)
        print(formed_event)
        current_user.add_event(formed_event)
        db.session.add(current_user)
        db.session.commit()
        flash("%s has been successfully added" % (formed_event.__class__.__name__))
        return redirect(url_for('index'))
    return render_template('add_event.html', event_type=event_type, form_type=formdict[event_type], form=form)

### VIEW EVENT PAGE ###
@app.route("/view_event/<id>", methods=["GET", "POST"])
@login_required
def view_event(id):
    viewthis = current_user.schedule.schedule_event_by_id(id)
    return render_template("view_event", e=viewthis)

### EDIT EVENT PAGE ###   
@app.route("/edit_event/<id>", methods=["GET", "POST"])
@login_required 
def edit_event(id):
    editthis = current_user.schedule.schedule_event_by_id(id)
    return render_template("edit_event", e=editthis)

### ERROR PAGES  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # go back to working database
    return render_template('500.html'), 500
    
if __name__ == "__main__":
    init_db()
