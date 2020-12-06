from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


@login.user_loader
def load_user(id):
    return Pushupchallenge_user.query.get(int(id))


class Pushupchallenge_user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    team = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Registration(db.Model):
    reg_id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer)
    player_id = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    dt = db.Column(db.Date)


class Team(db.Model):
    name = db.Column(db.String, primary_key=True)


class Exercise(db.Model):
    exercise_type_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(50))
    exercise_description = db.Column(db.String(250))
    maxrep = db.Column(db.Integer)


class Challenge(db.Model):
    challenge_id = db.Column(db.Integer, primary_key=True)
    challenge_navn = db.Column(db.String(50))
    challenge_description = db.Column(db.String(300))
    dt_from = db.Column(db.DateTime)
    dt_to = db.Column(db.DateTime)
