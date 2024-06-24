from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    name = db.Column(db.String(300))
    mimetype = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)         
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(300))
    firstName = db.Column(db.String(300))
    locked = db.Column(db.Boolean, default=False)
    audio_files = db.relationship('AudioFile')