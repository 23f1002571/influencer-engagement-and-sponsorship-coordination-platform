from flask import Flask,render_template,request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,User,AdRequest,Campaign,Request
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
    if user is None:
        return redirect(url_for('login'))
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
    return render_template('admin.html',user=user)    
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
    followers=request.form.get('followers')
    niche=request.form.get('niche')
    if username=='' or password=='' or name=='' or email=='':
        flash('Please fill all fields')
        return redirect(url_for('register_in'))
    if User.query.filter_by(username=username).first():
        flash('Username is already taken')
        return redirect(url_for('register_in'))
    if User.query.filter_by(email=email).first():
        flash('Email is already taken')
        return redirect(url_for('register_in'))
    user= User(username=username,password=password,name=name,email=email,role=role,platform=platform,followers=followers,niche=niche)
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
    followers=request.form.get('followers')
    niche=request.form.get('niche')
    if User.query.filter_by(username=username).first() and username != user.username:
        flash('Username is already taken')
        return redirect(url_for('profile'))
    user.username=username
    user.password=password
    user.name=name
    user.email=email
    user.platform=platform
    user.followers=followers
    user.niche=niche
    db.session.commit()
    flash("Profile updated")
    return redirect(url_for('index'))
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logout successfully")
    return redirect(url_for('login'))

@app.route('/stats')
@auth
def stats():
    return 'stats'
@app.route('/campaigns')
@auth
def campaigns():
    user = User.query.get(session['user_id'])
    campaigns = Campaign.query.filter_by(sponsor_id=user.user_id).all()
    return render_template('campaigns.html',campaigns=campaigns)  
@app.route('/campaign/register')
@auth
def register_campaign():
    campaign = Campaign()
    return render_template('campaign_register.html',campaign=campaign)

@app.route('/campaign/register', methods=['POST'])
def register_campaign_post():
    user=User.query.get(session['user_id'])
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    niche = request.form.get('niche')
    visibility = request.form.get('visibility')
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if name=='' or description=='' or start_date=='' or end_date=='' or budget=='' or visibility=='':
        flash('Please fill all fields')
        return redirect(url_for('register_campaign'))
    campaign= Campaign(name=name,description=description,start_date=start_date,end_date=end_date,budget=budget,visibility=visibility,sponsor_id=user.user_id,niche=niche)
    db.session.add(campaign)
    db.session.commit()
    flash('successfully registered')
    if user.is_admin:
        return redirect(url_for('find_camp'))
    else:
        return redirect(url_for('campaigns'))
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
    user = User.query.get(session['user_id'])
    if user.is_admin:
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
@app.route('/campaigns/<int:id>/delete')
@auth
def delete_campaign(id):
    user = User.query.get(session['user_id'])
    campaign = Campaign.query.get(id)
    if campaign and campaign.sponsor_id == user.user_id or user.is_admin:
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully')
    if user.is_admin:
        return redirect(url_for('find_camp'))
    else:
        return redirect(url_for('campaigns'))
@app.route('/campaigns/<int:id>/edit', methods=['GET', 'POST'])
@auth
def edit_campaign(id):
    user = User.query.get(session['user_id'])
    campaign = Campaign.query.get(id)
    if campaign and campaign.sponsor_id == user.user_id or user.is_admin:
        if request.method == 'POST':
            campaign.name = request.form['name']
            campaign.description = request.form['description']
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            campaign.budget = request.form.get('budget')
            campaign.visibility = request.form.get('visibility')
            campaign.start_date = datetime.strptime(start_date, "%Y-%m-%d")
            campaign.end_date = datetime.strptime(end_date, "%Y-%m-%d")
            db.session.commit()
            flash('Campaign updated successfully')
            if user.is_admin:
                return redirect(url_for('find_camp'))
            return redirect(url_for('campaigns'))
        return render_template('campaign_register.html', campaign=campaign)    
@app.route('/discover/campaigns', methods=['GET', 'POST'])
@auth
def dis_camp():
    if request.method == 'POST':
        para = request.form['para']
        query = request.form['search']
        if para == 'Name':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.name.like('%' + query + '%')).all()
        elif para == 'Description':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.description.like('%' + query + '%')).all()
        elif para == 'Budget':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.budget.like('%' + query + '%')).all()
        elif para == 'start_date':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.start_date.like('%' + query + '%')).all()
        elif para == 'end_date':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.end_date.like('%' + query + '%')).all()
        elif para == 'niche':
            campaigns = Campaign.query.filter_by(visibility='public').filter(Campaign.niche.like('%' + query + '%')).all()
        return render_template('dis_camps.html', campaigns=campaigns)
    else:
        campaigns = Campaign.query.filter_by(visibility='public').all()
        return render_template('dis_camps.html', campaigns=campaigns)
@app.route('/accepted_campaigns', methods=['GET'])
def accepted_campaigns():
    ad_requests = AdRequest.query.filter_by(influencer_id=session['user_id'], status='Pending').all()
    return render_template('accepted_campaigns.html', ad_requests=ad_requests)
  
@app.route('/campaign/<int:id>/accept', methods=['POST'])
def accept_campaign(id):
    campaign = Campaign.query.get(id)
    if campaign:
        ad_request = AdRequest(campaign_id=id, influencer_id=session['user_id'], requirements=campaign.description, payment_amount=campaign.budget, status='Pending')
        db.session.add(ad_request)
        db.session.commit()
        campaign.visibility = 'private'
        db.session.commit()
        flash('Ad request sent successfully')
        return redirect(url_for('accepted_campaigns')) 
@app.route('/campaign/<int:id>/done', methods=['POST'])
def done_campaign(id):
    ad_request = AdRequest.query.filter_by(campaign_id=id, influencer_id=session['user_id']).first()
    if ad_request:
        ad_request.status = 'Completed'
        db.session.commit()
        flash('Ad request marked as completed')
        return redirect(url_for('completed_ads'))
    else:
        flash('Ad request not found')
        return redirect(url_for('accepted_campaigns'))
@app.route('/completed_ads')
@auth
def completed_ads():
    ad_requests = AdRequest.query.filter_by(influencer_id=session['user_id'], status='Completed').all()
    return render_template('completed_ads.html', ad_requests=ad_requests)    
@app.route('/find_ads')
@auth
def find_ads():
    if User.query.get(session['user_id']).is_admin:
        ads = AdRequest.query.all()
        return render_template('find_ads.html', ads=ads)
    else:
        return "Access denied"    

@app.route('/discover/influencer', methods=['GET', 'POST'])
@auth
def dis_influ():
    if request.method == 'POST':
        para = request.form['para']
        query = request.form['search']
        if para == 'Username':
            users = User.query.filter_by(role='influencer').filter(User.username.like('%' + query + '%')).all()
        elif para == 'Name':
            users = User.query.filter_by(role='influencer').filter(User.name.like('%' + query + '%')).all()
        elif para == 'platform':
            users = User.query.filter_by(role='influencer').filter(User.platform.like('%' + query + '%')).all()
        elif para == 'followers':
            users = User.query.filter_by(role='influencer').filter(User.followers.like('%' + query + '%')).all()
        elif para == 'niche':
            users = User.query.filter_by(role='influencer').filter(User.niche.like('%' + query + '%')).all()
        return render_template('dis_influ.html', users=users)
    else:
        users = User.query.filter_by(role='influencer').all()
        return render_template('dis_influ.html', users=users)
@app.route('/request/influencer/<int:id>', methods=['GET', 'POST'])
@auth
def req_influ(id):
    if request.method == 'POST':
        para = request.form['para']
        query = request.form['search']
        if para == 'Username':
            users = User.query.filter_by(role='influencer').filter(User.username.like('%' + query + '%')).all()
        elif para == 'Name':
            users = User.query.filter_by(role='influencer').filter(User.name.like('%' + query + '%')).all()
        elif para == 'platform':
            users = User.query.filter_by(role='influencer').filter(User.platform.like('%' + query + '%')).all()
        elif para == 'followers':
            users = User.query.filter_by(role='influencer').filter(User.followers.like('%' + query + '%')).all()
        elif para == 'niche':
            users = User.query.filter_by(role='influencer').filter(User.niche.like('%' + query + '%')).all()
        return render_template('req_in.html', users=users, id=id)
    else:
        users = User.query.filter_by(role='influencer').all()
        return render_template('req_in.html', users=users, id=id)
@app.route('/create_request', methods=['POST'])
@auth
def create_request():
    campaign_id = request.form['campaign_id']
    influencer_id = request.form['influencer_id']
    new_request = Request(campaign_id=campaign_id, influencer_id=influencer_id)
    db.session.add(new_request)
    db.session.commit()
    flash('Request created successfully!')
    return redirect(url_for('req_influ', id=campaign_id))    
@app.route('/requests_in')
@auth
def requests_in():
    influencer_id = session['user_id']
    requests = Request.query.filter_by(influencer_id=influencer_id).all()
    return render_template('requests_in.html', requests=requests)
@app.route('/requests_sp')
@auth
def requests_sp():
    sponsor_id = session['user_id']
    requests = Request.query.join(Campaign).filter(Campaign.sponsor_id == sponsor_id).all()
    return render_template('requests_sp.html', requests=requests)
@app.route('/negotiate_request/<int:request_id>', methods=['POST'])
def negotiate_request(request_id):
    user=User.query.get(session['user_id'])
    new_price = request.form['new_price']
    db.session.query(Request).filter_by(request_id=request_id).update({'new_price': new_price})
    db.session.commit()
    if user.role=='influencer':
        return redirect(url_for('requests_in'))
    else:
        return redirect(url_for('requests_sp'))
@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    request = Request.query.get(request_id)
    user=User.query.get(session['user_id'])
    if request:
        db.session.delete(request)
        db.session.commit()
        flash('Request deleted successfully')
    if user.role=='influencer':        
        return redirect(url_for('requests_in'))
    else:
        return redirect(url_for('requests_sp'))
@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    request = Request.query.get(request_id)
    user=User.query.get(session['user_id'])
    if request and request.new_price!=None and user.role=='sponsor':
        request.sponsor_agreed=True
        db.session.commit()
        flash(' updated successfully')
    elif request and request.new_price==None and user.role=='sponsor':
        request.sponsor_agreed=True
        request.new_price=request.campaign.budget
        db.session.commit()
        flash(' updated successfully')
    elif request and request.new_price!=None and user.role=='influencer':
        request.influencer_agreed=True 
        db.session.commit()
        flash(' updated successfully')  
    elif request and request.new_price==None and user.role=='influencer':
        request.influencer_agreed=True
        request.new_price=request.campaign.budget  
        db.session.commit()
        flash(' updated successfully')  
    if request and request.new_price!=None and request.influencer_agreed==True and request.sponsor_agreed==True:
        new_ad_request = AdRequest(
            campaign_id=request.campaign_id,
            influencer_id=request.influencer_id,
            requirements=request.campaign.description,
            payment_amount=request.new_price,
            status='Pending'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        db.session.delete(request)
        db.session.commit()
        flash('Request accepted and AdRequest created')
    elif request and request.new_price==None and request.influencer_agreed==True and request.sponsor_agreed==True:
        new_ad_request = AdRequest(
            campaign_id=request.campaign_id,
            influencer_id=request.influencer_id,
            requirements=request.campaign.description,
            payment_amount=request.campaign.budget,
            status='Pending'
        ) 
        db.session.add(new_ad_request)
        db.session.commit()
        db.session.delete(request)
        db.session.commit()
        flash('Request accepted and AdRequest created')
    else:
        flash('Please wait for the other party to accept request')
    if user.role=='influencer':        
        return redirect(url_for('requests_in'))
    else:
        return redirect(url_for('requests_sp'))   
@app.route('/req_camp', methods=['POST'])
@auth
def req_camp():
    campaign_id = request.form['campaign_id']
    user = User.query.get(session['user_id'])
    new_request = Request(campaign_id=campaign_id, influencer_id=user.user_id)
    db.session.add(new_request)
    db.session.commit()
    flash('Request created successfully!')
    return redirect(url_for('dis_camp', id=campaign_id, user=user))