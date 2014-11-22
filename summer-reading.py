# all the imports
import sqlite3

# import flask
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# import sqlalchemy so we can use database classes
from flask.ext.sqlalchemy import SQLAlchemy

# include flask login so we get automatic login functionality
from flask.ext.login import (LoginManager, current_user, login_required, \
                             login_user, logout_user, UserMixin, \
                             confirm_login, fresh_login_required)

from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime

# configuration
WTF_CSRF_ENABLED = True
SECRET_KEY = 'readingisFun'
DATABASE = '/opt/summer-reading/db/summer-reading.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = '1234'

# create the app 
app = Flask(__name__)
app.config.from_object(__name__)

# create the db if it doesn't exist
db = SQLAlchemy(app)

# load settings from a config file instad, as an option
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#create login manager object
login_manager = LoginManager()
login_manager.init_app(app)

# redirect users to the login view when required 
login_manager.login_view = 'login'

# define how we're going to load a user object
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



# define the user class. Note this relies on the sqlalchemy plugin and flask_login
class User(db.Model):
    __tablename__ = "users"
    id = db.Column('id',db.Integer , primary_key=True)
    nickname = db.Column('nickname', db.String(20) ,unique=True , index=True)
    password = db.Column('password' , db.String(10))
    fullname = db.Column('fullname', db.String(50) ,index=True)
    full_librarycard = db.Column('full_librarycard', db.String(20))
    email = db.Column('email',db.String(50), index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
 
    def __init__(self , fullname ,nickname, password , full_librarycard, email):
        self.fullname = fullname
        self.nickname = nickname
        self.full_librarycard = full_librarycard
        self.password = password
        self.email = email.lower()
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)        
  
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True

    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.nickname)

# ---------------------------------
# functions
# ---------------------------------


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
    
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# ~~~~~~~~~~~ routes ~~~~~~~~~~~~~~~~ 
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, author, description, rating from books order by title desc')
    bookcountresult = g.db.execute('select count(1) from books')
    entries = [dict(title=row[0], author=row[1], description=row[2], rating=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

# allow insert of new book if the user is logged in 
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into books (username, title, author, description, rating) values (?, ?, ?, ?, ?)',
                 ["admin", request.form['title'], request.form['author'], request.form['description'], request.form['rating']])
    g.db.commit()
    flash('New book was successfully saved!')
    return redirect(url_for('show_entries'))

# Create new user login. GET loads the page, POST submits the new user details
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['name'] , request.form['nickname'], request.form['password'], request.form['full_librarycard'], request.form['email'])
    # add user via sqlalchemy 
    db.session.add(user)
    db.session.commit()
    flash("Successfully added user!")
    
    #g.db.execute('insert into users(fullname, nickname, password, full_librarycard, email) values (?,?,?,?,?)',
    #             user.name,user.nickname.user.password,user.full_librarycard,user.email)
        
    db.session.commit()
    flash('Welcome! you\'re successfully registered!')
    return redirect(url_for('login'))
 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    return redirect(url_for('index'))

# login 
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#           error = 'Invalid username'
#       elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
#            session['logged_in'] = True
#            flash('Welcome back to the Burnside Summer Reading Program!')
#            return redirect(url_for('show_entries'))
#    return render_template('login.html', error=error)

# logout 
#@app.route('/logout')
#def logout():
#    session.pop('logged_in', None)
#    flash('You were logged out')
#    return redirect(url_for('show_entries'))

# --------------- main --------------------     
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')