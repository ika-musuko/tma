from flask import render_template, flash, redirect, url_for, session, make_response, request
from app import app, db, lm
from flask_login import login_user, logout_user, current_user, login_required
from .auth import OAuthSignIn, GoogleSignIn
from .forms import EditForm
from .models import User


### HOME PAGE ###
@app.route('/')
@app.route('/index')
def index():
    # todo: get the user's current events and display them here
    return render_template('index.html')

### LOGIN PAGES ###
# standard google login
@app.route('/login/')
def login(provider):
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
    callback_crap = oauth.callback_base("google")
    print(str(callback_crap))
    social_id, email = callback_crap
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    nickname = email.split("@")[0]
    # get the user info
    user = User.query.filter_by(social_id=social_id).first()
    # if it's a new user, create it
    if user is None:
        user = User(social_id=social_id, nickname=nickname, email=email)
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
        current_user.nickname = form.nickname.data
        db.session.add(current_user)
        db.session.commit()
        flash("change success!")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = current_user.nickname
    return render_template('edit.html', form=form)
 
### ERROR PAGES  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # go back to working database
    return render_template('500.html'), 500
    