from flask import Flask
from flask import render_template, flash
from flask import request, session
from flask import redirect, url_for
from datetime import date, time
import login_operations as login_op
from event_operations import Events
from participant_ops import Student, Faculty, Outsider

app = Flask(__name__)

# We can render basic HTML from flask methods
# The flag before a function sets the route that will trigger the function
# Whatever is returned by the function will be rendered in the page

# The following secret key is used for verifying sessions
# Not really sure how it works though
app.secret_key = b'9HrfUeiAYXp3D^!m'

@app.route('/')
def index():
    event = Events()
    event_list = event.view_events()
    return render_template('index.html.jinja', events = event_list)


@app.route('/events')
def event_list_user():
    event = Events()
    event_list = event.view_events()
    return render_template('event_list_user.html.jinja', events = event_list)


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
        return render_template('login_form.html.jinja', status = status)


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

        if request.form['event_venue'] != '':
            args['venue'] = request.form['event_venue']
        else:
            args['venue'] = None

        if request.form['event_desc'] != '':
            args['description'] = request.form['event_desc']
        else:
            args['description'] = None

        date_ = request.form['event_date']
        time_ = request.form['event_time']
        args['date'] = date(int(date_[0:4]), int(date_[5:7]), int(date_[8:10]))
        if time_ != '':
            args['time'] = time_ + ':00'
        else:
            args['time'] = None
    
        if request.form['contact_name'] != '':
            args['contact_name'] = request.form['contact_name']
        else:
            args['contact_name'] = None

        if request.form['contact_num'] != '':
            args['contact_num'] = request.form['contact_num']
        else:
            args['contact_num'] = None

        event_obj.create_event(args)
        flash('Event Created Successfully')
        return redirect(url_for('event_list'))

    return render_template('addEvent.html.jinja')


@app.route('/modify_event/<int:event_id>', methods = ['POST', 'GET'])
def modify_event(event_id = 1):
    if 'username' not in session:
        return redirect(url_for('index'))

    event_obj = Events()

    prefil_data = {}
    row = event_obj.event_details(event_id)

    prefil_data['name'] = row[1]
    prefil_data['venue'] = row[2]
    prefil_data['desc'] = row[3]
    prefil_data['date'] = row[4]
    prefil_data['time'] = row[5]
    prefil_data['contact_name'] = row[6]
    prefil_data['contact_num'] = row[7]

    args = {}
    if request.method == 'POST':
        args['name'] = request.form['event_name']

        if request.form['event_venue'] != '':
            args['venue'] = request.form['event_venue']
        else:
            args['venue'] = None

        if request.form['event_desc'] != '':
            args['description'] = request.form['event_desc']
        else:
            args['description'] = None

        date_ = request.form['event_date']
        time_ = request.form['event_time']
        args['date'] = date(int(date_[0:4]), int(date_[5:7]), int(date_[8:10]))
        if time_ != '':
            args['time'] = time_ + ':00'
        else:
            args['time'] = None
    
        if request.form['contact_name'] != '':
            args['contact_name'] = request.form['contact_name']
        else:
            args['contact_name'] = None

        if request.form['contact_num'] != '':
            args['contact_num'] = request.form['contact_num']
        else:
            args['contact_num'] = None

        event_obj.modify_event(args, event_id)
        flash('Event Updated Successfully')
        return redirect(url_for('event_list'))

    return render_template('modifyEvent.html.jinja', data = prefil_data)


@app.route('/dashboard')
def admin_dash():
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template('Dashboard.html.jinja')


@app.route('/event_list')
def event_list():
    if 'username' not in session:
        return redirect(url_for('index'))

    event_obj = Events()
    all_events = event_obj.view_events()
    return render_template('event_list.html.jinja', all_events = all_events)


@app.route('/event/<int:event_id>')
def event(event_id = 1):
    if 'username' not in session:
        return redirect(url_for('index'))

    event_obj = Events()
    context = event_obj.event_details(event_id)

    event_obj = Events()
    students = event_obj.event_students(event_id)

    event_obj = Events()
    faculties = event_obj.event_faculty(event_id)

    event_obj = Events()
    outsiders = event_obj.event_outsider(event_id)

    if context == None:
        flash('Event Not Found')
        return redirect(url_for('event_list'))

    return render_template('event.html.jinja', event_row = context, 
                                               students = students,
                                               faculties = faculties,
                                               outsiders = outsiders)


@app.route('/register/<string:ptype>/<int:event_id>', methods = ['POST', 'GET'])
def register(ptype = 'student', event_id = 1):
    event = Events()
    event_name = event.event_details(event_id)[1]

    participant_obj = None
    if ptype == 'faculty':
        participant_obj = Faculty()
        args = {}
        if request.method == 'POST':
            args['fid'] = request.form['fid']
            args['name'] = request.form['name']

            if request.form['contact_num'] != '':
                args['contact_no'] = request.form['contact_num']
            else:
                args['contact_no'] = None

            if request.form['dept'] != '':
                args['dept'] = request.form['dept']
            else:
                args['dept'] = None

            participant_obj.register_faculty(faculty_args = args, event_id = event_id)

    elif ptype == 'outsider':
        participant_obj = Outsider()
        args = {}
        if request.method == 'POST':
            args['govt_id'] = request.form['govt_id']
            args['name'] = request.form['name']

            if request.form['contact_num'] != '':
                args['contact_num'] = request.form['contact_num']
            else:
                args['contact_num'] = None

            if request.form['college'] != '':
                args['college'] = request.form['college']
            else:
                args['college'] = None

            if request.form['state'] != '':
                args['state'] = request.form['state']
            else:
                args['state'] = None

            participant_obj.register_outsider(outsider_args = args, event_id = event_id)

    else:
        ptype = 'student'
        participant_obj = Student()
        args = {}
        if request.method == 'POST':
            args['roll_no'] = request.form['roll']
            args['name'] = request.form['name']

            if request.form['contact_num'] != '':
                args['contact_num'] = request.form['contact_num']
            else:
                args['contact_num'] = None

            if request.form['email'] != '':
                args['email'] = request.form['email']
            else:
                args['email'] = None

            if request.form['dept'] != '':
                args['dept'] = request.form['dept']
            else:
                args['dept'] = None

            if request.form['sem'] != '':
                args['sem'] = request.form['sem']
            else:
                args['sem'] = None

            participant_obj.register_student(student_args = args, event_id = event_id)

    return render_template('register.html.jinja', ptype = ptype, event_id = event_id, event_name = event_name)