from flask import render_template, flash, redirect, url_for, session, make_response, request
from . import app, db, login_manager
from flask_login import login_user, logout_user, current_user, login_required
from .auth import OAuthSignIn
from .forms import isblank, form_to_event, EditForm, EventForm, SleepScheduleForm, RecurringEventForm, TaskEventForm, if_filled, formdict, edit_form_with_args
from .models import init_db, User, UserEvent, UserScheduleEvent, to_event
from .scheduler import event, schedule, txt
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

### HELP PAGE ###
@app.route('/help/')
def help():
    return render_template('help.html')
 
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
    form = EditForm(nickname=current_user.nickname, reminder_frequency=current_user.reminder_frequency)
    if form.validate_on_submit():
        current_user.nickname           = if_filled(form.nickname.data, current_user.nickname)
        current_user.email              = if_filled(form.email.data, current_user.email)
        current_user.phone              = if_filled(''.join(c for c in form.phone.data if c.isdigit()), current_user.phone)
        current_user.cellphone_provider = if_filled(form.cellphone_provider.data, current_user.cellphone_provider)
        #current_user.reminder_frequency = if_filled(form.reminder_frequency, current_user.reminder_frequency)
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

### EDIT QUEUE PAGE ###
@app.route('/edit_queue/', methods=['GET', 'POST'])
@app.route('/edit_queue/<int:page>', methods=['GET', 'POST'])
@login_required
def edit_queue(page=1):
    events = current_user.events.paginate(page, EVENTS_PER_PAGE, False)
    return render_template('edit_queue.html', event_queue=events)

### EDIT EVENT PAGE ###
@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event_query = current_user.events.filter_by(id=id).first()
    if event_query == None:
        flash('Event ID: %i was not found' % id)
        return redirect(url_for('edit_queue'))
    form = edit_form_with_args(event_query)
    if form.validate_on_submit():
        if event_query.type == "RecurringEvent": 
            event_query.name                   = form.name.data                                      
            event_query.desc                   = form.desc.data                 
            event_query.recEvent_period_start  = form.period_start.data
            event_query.recEvent_period_end    = form.period_end.data  
            event_query.recEvent_start_time    = form.start_time.data  
            event_query.recEvent_end_time      = form.end_time.data    
            event_query.recEvent_daystr        = ''.join(c for c in form.days.data if c in "NMTWHFS")
        
        elif event_query.type == "SleepEvent":
            event_query.recEvent_start_time    = form.sleep.data
            event_query.recEvent_end_time      = form.wake.data
        
        elif event_query.type == "TaskEvent":
            event_query.name                  = form.name.data    
            event_query.desc                  = form.desc.data    
            event_query.taskEvent_duration    = form.duration.data
            event_query.taskEvent_done        = form.done.data    
            
        elif event_query.type == "DueEvent":
            event_query.name                  = form.name.data    
            event_query.desc                  = form.desc.data    
            event_query.dueEvent_due          = form.due.data     
            event_query.taskEvent_duration    = form.duration.data
            event_query.taskEvent_done        = form.done.data    
            
        else:
            event_query.name     = form.name.data  
            event_query.desc     = form.desc.data  
            event_query.start    = form.start.data 
            event_query.end      = form.end.data   
        
        db.session.commit()
        update_schedule_helper()
        flash("%s: %i has been successfully edited" % (event_query.type, event_query.id))
        return redirect(url_for('edit_queue'))
    return render_template("edit_event.html", form=form, id=id)
        
        
### RESCHEDULE TASK ###
@app.route('/reschedule_task/<int:id>', methods=['GET','POST'])
@login_required
def reschedule_task(id):
    pass
    
### DELETE EVENT ###
@app.route('/delete_event/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    query = current_user.events.filter_by(id=id)
    if query.first() == None:
        flash('Event ID: %i was not found' % id)
        return redirect(url_for('edit_queue'))
    query.delete()
    db.session.commit()
    flash('Event ID: %i has been deleted' % id)
    return redirect(url_for('edit_queue'))    

## misc    
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
@app.route("/delete_schedule_event/<int:id>", methods=["GET", "POST"])
@login_required 
def delete_schedule_event(id):
    query = current_user.scheduleevents.filter_by(id=id)
    if query.first() == None:
        flash('Schedule Event ID: %i was not found' % id)
        return redirect(url_for('index'))
        
    query.delete()
    db.session.commit()
    flash('Schedule Event ID: %i has been deleted' % id)
    return redirect(url_for('index'))    

### EDIT SCHEDULE EVENT PAGE ###   
@app.route("/edit_schedule_event/<int:id>", methods=["GET", "POST"])
@login_required 
def edit_schedule_event(id):
    event_query = current_user.scheduleevents.filter_by(id=id).first()
    if event_query == None:
        flash('ScheduleEvent ID: %i was not found' % id)
        return redirect(url_for('index'))
    form = EventForm(
                      name   = event_query.name    
                     ,desc   = event_query.desc 
                     ,start  = event_query.start
                     ,end    = event_query.end  
                    )
    if form.validate_on_submit():
        event_query.name  = form.name.data 
        event_query.desc  = form.desc.data 
        event_query.start = form.start.data
        event_query.end   = form.end.data  
        db.session.add(event_query)
        db.session.commit()
        flash('Schedule Event ID: %i has been edited' % id)
        return redirect(url_for('index'))
    return render_template("edit_schedule_event.html", id=event_query.id, form=form)


@app.route("/send_reminders/", methods=["GET","POST"])
@login_required
def send_reminders():
    '''
    sends an email or text message (via multimedia message) of the schedule in a more abbreviated way
    '''
    getactual = current_user.scheduleevents.filter(UserScheduleEvent.end >= datetime.datetime.today()).limit(10).all()
    event_list = [se.msg_print for se in getactual]
    message = "Schedule:\n\n"+'\n'.join(event_list)
    status = ""
    if not (isblank(current_user.cellphone_provider) or isblank(current_user.phone)):
        txt.send_email(message, current_user.txt_address)
        status += "Phone"
    if not isblank(current_user.email):
        txt.send_email(message, current_user.email)
        status += "Email" if status == "" else " and Email"
    if status == "": status = "No"
    flash("%s Reminders sent!" % status)
    return redirect(url_for('index'))

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
