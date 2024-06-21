from flask import Flask,render_template,request,redirect,url_for,flash,session
from models import db,User,AdRequest,Campaign
from functools import wraps
from app import app
def auth(func):
    @wraps(func)
    def inner(*agrs,**kwargs):
        if 'user_id'not in session:
            flash('Login to continue')
            return redirect(url_for('login'))
        return func(*agrs ,**kwargs)
    return inner 
@app.route('/')
@auth
def index():
    return render_template('index.html',user=User.query.get(session['user_id']))
@app.route('/profile')
@auth
def profile():
    return render_template('profile.html',user=User.query.get(session['user_id']))
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login_post():
    username= request.form.get('username')
    password= request.form.get('password')
    if username=='' or password=='':
        flash('Please fill all fields')
        return redirect(url_for('login'))
    user=User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid username')
        return redirect(url_for('login'))
    if not user.check_pass(password):
        flash('Invalid password')
        return redirect(url_for('login'))
    session['user_id']=user.user_id 
    return redirect(url_for('index'))
@app.route('/register/influencer')
def register_in():
    return render_template('register_in.html')
@app.route('/register/influencer', methods=['POST'])
def register_in_post():
    username= request.form.get('username')
    name= request.form.get('name')
    password= request.form.get('password')
    if username=='' or password=='' or name=='':
        flash('Please fill all fields')
        return redirect(url_for('register_in'))
    if User.query.filter_by(username=username).first():
        flash('Username is already taken')
        return redirect(url_for('register_in'))
    user= User(username=username,password=password,name=name)
    db.session.add(user)
    db.session.commit()
    flash('successfully registered')
    return redirect(url_for('login'))
@app.route('/profile',methods=['POST'])
def post_in_post():
    user=User.query.get(session['user_id'])
    username= request.form.get('username')
    name= request.form.get('name')
    password= request.form.get('password')
    if username=='' or password=='' or name=='':
        flash('Please fill all fields')
        return redirect(url_for('profile'))
    if User.query.filter_by(username=username).first() and username != user.username:
        flash('Username is already taken')
        return redirect(url_for('profile'))
    user.username=username
    user.password=password
    user.name=name
    db.session.commit()
    flash("Profile updated")
    return redirect(url_for('profile'))
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logout successfully")
    return redirect(url_for('login'))

@app.route('/stats')
@auth
def stats():
    return "stats"   
@app.route('/find')
@auth
def find():
    return "find"  