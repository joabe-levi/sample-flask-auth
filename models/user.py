from database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(100), nullable=True, default='user')
    
    def __str__(self):
        return f'{self.username}'

    def save(self, *args, **kwargs):
        db.session.add(self)
        db.session.commit()

    def delete(self, *args, **kwargs):
        db.session.delete(self)
        db.session.commit()
