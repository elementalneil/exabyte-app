from flask import Flask
from flask import render_template
from flask import request, session
from flask import redirect, url_for
from datetime import date, time
import login_operations as login_op
from event_operations import Events

app = Flask(__name__)

# We can render basic HTML from flask methods
# The flag before a function sets the route that will trigger the function
# Whatever is returned by the function will be rendered in the page

# The following secret key is used for verifying sessions
# Not really sure how it works though
app.secret_key = b'9HrfUeiAYXp3D^!m'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def users_list():
    login_obj = login_op.LoginPage()
    usernames = login_obj.return_accounts()
    render = '<h1>Users: </h1>'

    render = render + '<ul>'
    for user in usernames:
        render = render + '<li>' + user + '</li>'

    render = render + '</ul>'

    return render

@app.route('/login', methods = ['POST', 'GET'])
def login(status = 0):
    if 'username' in session:
        return redirect(url_for('index'))

    login_obj = login_op.LoginPage()

    if request.method == 'POST':
        status = login_obj.login(request.form['username'], 
                                 request.form['password'])

    if status == 1:
        # Creates a new session
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template('login_form.html', status = status)


@app.route('/logout')
def logout():
    # Deletes an existing session
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/add_event', methods = ['POST', 'GET'])
def create_event():
    if 'username' not in session:
        return redirect(url_for('index'))

    event_obj = Events()

    args = {}
    if request.method == 'POST':
        args['name'] = request.form['event_name']
        args['venue'] = request.form['event_venue']

        date_ = request.form['event_date']
        time_ = request.form['event_time']
        args['date'] = date(int(date_[0:4]), int(date_[5:7]), int(date_[8:10]))
        args['time'] = time_ + ':00'
    
        args['contact_name'] = request.form['contact_name']
        args['contact_num'] = request.form['contact_num']

        event_obj.create_event(args)

    # args = {}
    # # if request.method == 'POST':
    # args['name'] = 'Proshow2'
    # args['venue'] = 'Football Ground'
    # args['date'] = date(2022, 10, 25)
    # args['time'] = '07:30:00'
    # args['contact_name'] = 'John Doe'
    # args['contact_num'] = '+91 815 568 9973'

    return render_template('addEvent.html')


@app.route('/event')
def event():
    return render_template('event.html')