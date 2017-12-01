from flask import render_template, flash, redirect, url_for, session, make_response, request
from . import app, db, login_manager
from flask_login import login_user, logout_user, current_user, login_required
from .auth import OAuthSignIn
from .forms import form_to_event, EditForm, EventForm, SleepScheduleForm, RecurringEventForm, TaskEventForm, if_filled
from .models import init_db, User, UserEvent, UserScheduleEvent, to_event
from .scheduler import event, schedule
import datetime

EVENTS_PER_PAGE = 10

### HOME PAGE ###
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    if current_user.is_authenticated: 
        # get the user's current events and display them here
        schedule_events = current_user.scheduleevents.filter(UserScheduleEvent.end >= datetime.datetime.today()).paginate(page, EVENTS_PER_PAGE, False)
        #schedule_events = current_user.scheduleevents.paginate(page, EVENTS_PER_PAGE, False)
        return render_template('index.html', todolist=schedule_events)
    else:
        return render_template('index.html')

### EDIT QUEUE PAGE ###

@app.route('/edit_queue/', methods=['GET', 'POST'])
@app.route('/edit_queue/<int:page>', methods=['GET', 'POST'])
@login_required
def edit_queue(page=1):
    events = current_user.events.paginate(page, EVENTS_PER_PAGE, False)
    event_forms = []
    # TODO: make everything into forms
    for e in events.items:
        #event_forms.append(formdict[type]
        pass
    return render_template('edit_queue.html', event_forms=event_forms, event_queue=events)

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
            'regular'   : EventForm 
           ,'sleep'     : SleepScheduleForm  # sleep should redirect to editing the sleep schedule but for now it is left here
           ,'recurring' : RecurringEventForm
           ,'task'      : TaskEventForm
    }
    form = formdict[event_type]()
    if form.validate_on_submit():
        formed_event = form_to_event(form)
        print(formed_event)
        user_event = event_to_userevent(formed_event)
        if user_event is not None:  
            db.session.add(user_event)
            db.session.commit()
            update_schedule_helper()
            flash("%s has been successfully added" % (formed_event.__class__.__name__))
        else:
            flash("Error in adding event")
        return redirect(url_for('index'))
    return render_template('add_event.html', event_type=event_type, form_type=formdict[event_type], form=form)

def event_to_userevent(formed_event):
    ftype = type(formed_event)
    user_event = None
    if ftype == event.Event: 
        user_event =    UserEvent(
                                     author=current_user
                                    ,type="Event"
                                    ,name=formed_event.name
                                    ,desc=formed_event.desc
                                    ,priority=formed_event.priority
                                    ,start=formed_event.start
                                    ,end=formed_event.end
                                )
    elif ftype == event.RecurringEvent or ftype == event.SleepEvent:  
        user_event =    UserEvent(
                                     author=current_user
                                    ,type="RecurringEvent" if ftype == event.RecurringEvent else "SleepEvent"
                                    ,name=formed_event.name
                                    ,desc=formed_event.desc
                                    ,priority=formed_event.priority
                                    ,recEvent_period_start=formed_event.period_start
                                    ,recEvent_period_end=formed_event.period_end
                                    ,recEvent_start_time=formed_event.start_time
                                    ,recEvent_end_time=formed_event.end_time
                                    ,recEvent_daystr=formed_event.days
                                )
    elif ftype == event.TaskEvent:
        user_event =     UserEvent(
                                     author=current_user
                                    ,type="TaskEvent"
                                    ,name=formed_event.name
                                    ,desc=formed_event.desc
                                    ,priority=formed_event.priority
                                    ,taskEvent_done=formed_event.done
                                    ,taskEvent_duration=formed_event.duration
                                )
    elif ftype == event.DueEvent: 
        user_event =    UserEvent(
                                     author=current_user
                                    ,type="DueEvent"
                                    ,name=formed_event.name
                                    ,desc=formed_event.desc
                                    ,priority=formed_event.priority
                                    ,taskEvent_done=formed_event.done
                                    ,taskEvent_duration=formed_event.duration
                                    ,dueEvent_due=formed_event.due
                                )
    return user_event

### UPDATE SCHEDULE ###  
@app.route("/update_schedule/", methods=["GET", "POST"])
@login_required
def update_schedule():
    update_schedule_helper()
    flash("Schedule has been updated")
    return redirect(url_for('index'))
    
def update_schedule_helper():
    # 1. make a list of all events from the events table
    database_events = current_user.events.all()
    events = [to_event(de) for de in database_events]
    
    # 2. write to a new schedule.Schedule object
    sched = schedule.Schedule(events, start=datetime.datetime.today(), end=datetime.datetime.today()+datetime.timedelta(days=90))
    
    # 3. wipe current user's schedule events from schedulevents table
    current_user.scheduleevents.delete()
    
    # 4. write new events
    for se in sched.schedule_event_data:
        database_schedule_event = UserScheduleEvent(author=current_user, name=se.name, desc=se.desc, extra_info=se.extra_info, start=se.start, end=se.end)
        db.session.add(database_schedule_event)

    # 5. commit database
    db.session.commit()

    
TEST_EVENT = schedule.ScheduleEvent(start=datetime.datetime.today(), end=datetime.datetime.today()+datetime.timedelta(hours=2), name="test event", desc="description lol", extra_info="extra info!", parent_id=1)    

### DELETE SCHEDULE EVENT ###   
@app.route("/delete_schedule_event/<id>", methods=["GET", "POST"])
@login_required 
def delete_schedule_event(id):
    pass

### EDIT SCHEDULE EVENT PAGE ###   
@app.route("/edit_schedule_event/<id>", methods=["GET", "POST"])
@login_required 
def edit_schedule_event(id):
    editthis = TEST_EVENT
    return render_template("edit_schedule_event", e=editthis)

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
