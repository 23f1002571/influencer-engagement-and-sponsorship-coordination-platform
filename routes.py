from flask import Flask,render_template,request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,User,AdRequest,Campaign
from functools import wraps
from datetime import datetime
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
    user=User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    else:
        if user.role=='influencer':
            return render_template('index_in.html',user=user)
        else:
            return render_template('index_sp.html',user=user)
@app.route('/admin')
@auth
def admin():
    user=User.query.get(session['user_id'])
    us=User.query.all()
    return render_template('admin.html',user=user,us=User.query.all())    
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
    username = request.form.get('username')
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    platform = request.form.get('platform')
    if username=='' or password=='' or name=='' or email=='':
        flash('Please fill all fields')
        return redirect(url_for('register_in'))
    if User.query.filter_by(username=username).first():
        flash('Username is already taken')
        return redirect(url_for('register_in'))
    if User.query.filter_by(email=email).first():
        flash('Email is already taken')
        return redirect(url_for('register_in'))
    user= User(username=username,password=password,name=name,email=email,role=role,platform=platform)
    db.session.add(user)
    db.session.commit()
    flash('successfully registered')
    return redirect(url_for('login'))
@app.route('/profile',methods=['POST'])
def post_in_post():
    user=User.query.get(session['user_id'])
    username= request.form.get('username')
    name= request.form.get('name')
    email = request.form.get('email')
    platform = request.form.get('platform')
    password= request.form.get('password')
    if User.query.filter_by(username=username).first() and username != user.username:
        flash('Username is already taken')
        return redirect(url_for('profile'))
    user.username=username
    user.password=password
    user.name=name
    user.email=email
    user.platform=platform
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
@app.route('/campaigns')
@auth
def campaigns():
    return render_template('campaigns.html')  
@app.route('/campaign/register')
def register_campaign():
    return render_template('campaign_register.html')

@app.route('/campaign/register', methods=['POST'])
def register_campaign_post():
    user=User.query.get(session['user_id'])
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if name=='' or description=='' or start_date=='' or end_date=='' or budget=='' or visibility=='':
        flash('Please fill all fields')
        return redirect(url_for('register_campaign'))
    campaign= Campaign(name=name,description=description,start_date=start_date,end_date=end_date,budget=budget,visibility=visibility,sponsor_id=user.user_id)
    db.session.add(campaign)
    db.session.commit()
    flash('successfully registered')
    return redirect(url_for('index'))
@app.route('/find')
@auth
def find():
    if User.query.get(session['user_id']).is_admin:
        users = User.query.all()
        return render_template('find.html', users=users)
    else:
        return "Access denied"
@app.route('/find_camp')
@auth
def find_camp():
    if User.query.get(session['user_id']).is_admin:
        campaigns = Campaign.query.all()
        return render_template('find_camp.html', campaigns=campaigns)
    else:
        return "Access denied"


@app.route('/user/<int:id>/delete')
@auth
def delete_user(id):
    current_user = User.query.get(session['user_id'])
    if current_user.is_admin:
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
        return redirect(url_for('find'))
    else:
        flash('Access denied')
        return redirect(url_for('find'))

@app.route('/user/<int:id>', methods=['GET', 'POST'])
@auth
def edit_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.name = request.form['name']
        user.email = request.form['email']
        user.platform = request.form['platform']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('find'))
    return render_template('profile.html', user=user)