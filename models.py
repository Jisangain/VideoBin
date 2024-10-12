from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class Base(db.Model):
    baseurl = db.Column(db.String(80), primary_key=True)
    mainurl = db.Column(db.String(80), nullable=False)
    make_public = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(80))
    link_type = db.Column(db.Integer, nullable=False)
    ad_percent = db.Column(db.Integer, default=50)
    creation_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = relationship('User', backref='bases', cascade="all, delete")

    def __repr__(self):
        return f'<Base {self.baseurl}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    name = db.Column(db.String(100))
    btc_address = db.Column(db.String(100))
    usd_balance = db.Column(db.Float)
    creation_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.email}>'

class countlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="SET DEFAULT"), nullable=False, default=1)
    viewcount = db.Column(db.Integer, nullable=False)
    usd_balance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<adlog {self.time}>'

class distributionlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="SET DEFAULT"), nullable=False, default=1)
    usd_balance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<distributelog {self.usd_balance}>'

class IPAccess(db.Model):
    ip = db.Column(db.String(45), primary_key=True)  # IPv6-compatible
    time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<IPAccess {self.ip}>'