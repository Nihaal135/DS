
import os
from flask import Flask, render_template, request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from sqlalchemy.orm import session

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = 'signin'

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.Text)
    location = db.Column(db.Text)
    def __init__(self, company, location):
        self.company = company
        self.location = location


class User(db.Model,UserMixin) :

    __tablename__ = "userstable"

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)     

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get((user_id))
 

##############################################


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        user = User(email=request.form.get('email'),
                    password=request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('login.html')
    


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get('email')).first()

        # Check that the user was supplied and the password is right
        # The check_password method comes from the User object
        if user is not None and user.check_password(request.form.get('password')):

            #Log in the user
            login_user(user)

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('index')

            return redirect(next)
    return render_template('signin.html')


@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login')
def login():
    return render_template("home.html")

@app.route('/logout')

def logout():
    return render_template("login.html")    

@app.route('/markComplete1')
def markComplete1():
    return render_template('MarkComplete.html')

@app.route('/markComplete',methods=["GET","POST"])
def markComplete():
    if request.method == 'POST':
        print('entered mark complete function')
        markid = request.form.get("mark_id")
        print("id:",markid)
        todo = db.session.query(Company).filter(company=markid).first()
        todo.complete = not todo.complete #toggle true/false for complete
        if todo.complete == False:
            todo.title = "<del>" + todo.title + "</del>" # add strikethrough tags to title
            db.session.commit()
        else:
            db.session.commit()
        
    return render_template('index.html')

@app.route('/update1')
def update1():
     return render_template('update.html')

@app.route('/delete1')
def delete1():
     return render_template('delete.html')

@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        print('entered update function')
        update_id = int(request.form.get("id"))
        update_name = request.form.get("nameOfCompany")
        update_location = request.form.get("location")
        print("id:",update_id)
        print("name:",update_name)
        print("location:",update_location)
        result=db.session.query(Company).filter(Company.id==update_id).update({Company.location:update_location},synchronize_session=False)
        print("rows updated:",result)
        db.session.commit()

    return render_template('index.html')



@app.route('/delete',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        print('entered delete function')
        delid = request.form.get("del_id")
        print("id:",delid)
        del_obj=db.session.query(Company).filter(Company.id==delid).delete()
        #del_obj=db.session.query(Company).delete()
        print("rows deleted",del_obj)
        db.session.commit()
    return render_template('index.html')



@app.route('/add', methods=["GET", "POST" ])
def index():
    if request.method == 'POST':
        company = request.form.get("company")
        location = request.form.get("location")
        print("comany:",company)
        print("location:",location)
        new_company = Company(company, location)
        db.session.add(new_company)
        db.session.commit()
        
    return render_template('index.html')

  

@app.route('/display', methods=['GET', 'POST'])
def display():
    companies = Company.query.all()
    print(companies)
    return render_template('display.html', var=companies)

if __name__ == '__main__':
    app.run(debug=True)