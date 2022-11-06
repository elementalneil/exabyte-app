from flask import Flask
from flask import render_template
from flask import request, session
from flask import redirect, url_for
import login_operations as login_op

app = Flask(__name__)

# We can render basic HTML from flask methods
# The flag before a function sets the route that will trigger the function
# Whatever is returned by the function will be rendered in the page

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
    login_obj = login_op.LoginPage()

    if request.method == 'POST':
        status = login_obj.login(request.form['username'], 
                                 request.form['password'])

    if status == 1:
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template('login_form.html', status = status)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))