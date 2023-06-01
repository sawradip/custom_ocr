from datetime import datetime
from flaskapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    entries = db.relationship('Entry', backref='uploader', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    report_img = db.Column(db.Text, nullable=False)
    report_img_name = db.Column(db.Text, nullable=False)
    report_text = db.Column(db.Text, nullable=False)
    report_positional_info = db.Column(db.Text, nullable=False)
    comment =  db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Entry('{self.company_name}', '{self.date_posted}')"