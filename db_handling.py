from ctypes import ARRAY
from datetime import datetime
from exts import db
#pour hacher le mtp
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func
from db_config import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20),  nullable=False)
    lastname = db.Column(db.String(20),  nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(20))
    garments = db.relationship('Garment', backref='seller', lazy=True)
    messages = db.relationship('Message', backref='sender', lazy=True)
    cart= db.relationship('Achat')
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def set_password(self, secret):
        self.password = generate_password_hash(secret)

    def check_password(self, secret):
        return check_password_hash(self.password, secret)




class Garment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(5), nullable=False)
    size = db.Column(db.String(5), nullable=False)
    price = db.Column(db.INTEGER, nullable=False)
    des = db.Column(db.Text, nullable=False)
    pic = db.Column(db.String(2000), nullable=False, default='default.jpg')
    #db.Column(ARRAY(db.Text), nullable=False, default=db.cast(array([], type_=db.Text), ARRAY(db.Text)))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Garment('{self.title}', '{self.date_posted}')"





    
class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    gar_name = db.Column(db.Text, nullable=False)
    msg = db.Column(db.Text, nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)	
    


class Achat(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    uid= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gid= db.Column(db.Integer, db.ForeignKey('garment.id'), nullable=False)
    date= db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

"""class Cart(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    uid= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achats= db.relationship('Achat')"""






    
