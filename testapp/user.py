from testapp import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'mas_user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)