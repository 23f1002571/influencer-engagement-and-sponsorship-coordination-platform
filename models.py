from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    is_admin=db.Column(db.Boolean, nullable=False, default= False)
    flag=db.Column(db.Boolean, nullable=True, default= False)
    email = db.Column(db.String(120), nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(16), nullable=False)
    platform = db.Column(db.String(64), nullable=True ,default= 'None')
    followers=db.Column(db.Integer, nullable=True ,default= '1')
    niche=db.Column(db.String(64), nullable=True ,default= 'None')
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)
    @property
    def password(self):
        raise AttributeError('Dont have permission')
    @password.setter
    def password(self,password):
        self.passhash=generate_password_hash(password)
    def check_pass(self,password):
        return check_password_hash(self.passhash,password)    
class Campaign(db.Model):
    __tablename__ = 'campaign'
    Campaign_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(8), nullable=False)
    niche=db.Column(db.String(64), nullable=True ,default= 'None')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    flag=db.Column(db.Boolean, nullable=True, default= False)

class AdRequest(db.Model):
    __tablename__ = 'adrequest'
    Ad_id = db.Column(db.Integer, primary_key=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(16), nullable=False, default='Pending')
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.Campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
class Request(db.Model):
    __tablename__ = 'request'
    request_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.Campaign_id'), nullable=False)
    campaign = db.relationship('Campaign', backref=db.backref('requests', lazy=True))
    influencer_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    new_price = db.Column(db.Integer, nullable=True)
    influencer_agreed = db.Column(db.Boolean, default=False)
    sponsor_agreed = db.Column(db.Boolean, default=False)
