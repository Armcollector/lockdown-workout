import os
import urllib.parse

import pyodbc
from flask_login import current_user
from sqlalchemy import create_engine

from app.models import Registration, Team

from . import db


def get_engine():
    connstr = os.environ.get("DB_CONNECTIONSTRING")

    params = urllib.parse.quote_plus(connstr)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine


def getconnection():
    conn_str = os.environ["DB_CONNECTIONSTRING"]
    cnxn = pyodbc.connect(conn_str)
    return cnxn


def upsert(exercise_id, player_id, reps, dt):

    exists = Registration.query.filter_by(
        exercise_id=exercise_id,
        player_id=current_user.id,
        dt=dt,
    ).first()

    if exists:
        exists.reps = reps
    else:
        new = Registration(
            exercise_id=exercise_id, player_id=current_user.id, reps=reps, dt=dt
        )
        db.session.add(new)

    db.session.commit()


def getteams():
    teams = Team.query.all()

    return [t.name for t in teams]
