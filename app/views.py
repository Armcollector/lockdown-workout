"""
Routes and views for the flask application.
"""

from datetime import date, datetime, timedelta

import pandas as pd
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

import app.dataanalysis as da
import app.databasefunctions as dbfunc
import app.forms as forms
from app import app
from app.databasefunctions import upsert
from app.models import Exercise, Pushupchallenge_user, Registration

from . import app, cache, db


def common_items():
    d = {}
    d["maintitle"] = app.config["MAINTITLE"]
    return d


@app.route("/")
@app.route("/home")
@app.route("/index")
def index():

    return render_template(
        f"{app.config['INSTANCE']}_index.html",
        title="Hjem",
        year=datetime.now().year,
        **common_items(),
    )


def get_exercises(delta):
    registered_exercises = Registration.query.filter_by(
        player_id=current_user.id, dt=date.today() - timedelta(days=delta)
    ).all()

    if not registered_exercises:
        return [0, 0, 0, 0]
    else:
        return [r.reps for r in registered_exercises]


@app.route("/logpushups/", methods=["GET", "POST"])
@login_required
def logpushups():
    form = forms.Logpushups()

    if form.validate_on_submit():
        flash("Lagret ny status.")

        upsert(
            0,
            player_id=current_user.id,
            reps=min(form.sit_reps.data, 250),
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            1,
            player_id=current_user.id,
            reps=min(form.air_reps.data, 150),
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            2,
            player_id=current_user.id,
            reps=min(form.push_reps.data, 70),
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            3,
            player_id=current_user.id,
            reps=min(form.pull_reps.data, 30),
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )

    registered_exercises = [get_exercises(0), get_exercises(1), get_exercises(2)]

    exercises = {
        0: form.sit_reps,
        1: form.air_reps,
        2: form.push_reps,
        3: form.pull_reps,
    }

    for i, ex in enumerate(registered_exercises[0]):
        exercises[i].data = ex

    form.dt.data = date.today()

    if not form.day.data:
        form.day.data = 0

    return render_template(
        "logpushups.html",
        title="Log øvelser",
        year=datetime.now().year,
        message="Her kan du registrere.",
        player_id=current_user.id,
        playername=current_user.username,
        form=form,
        today=date.today(),
        exercises=registered_exercises,
        **common_items(),
    )


@app.route("/registeruser", methods=["GET", "POST"])
def registeruser():
    form = forms.RegisterUser()

    if form.validate_on_submit():
        user = Pushupchallenge_user(
            username=form.username.data, email=form.email.data, team=form.team.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        return redirect(url_for("logpushups"))

    return render_template(
        "registeruser.html",
        title="Registrer bruker",
        year=datetime.now().year,
        message="Ny brukerside.",
        form=form,
        **common_items(),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = forms.LoginForm()

    if form.validate_on_submit():
        user = Pushupchallenge_user.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form, **common_items())


@app.route("/whatsnew")
def whatsnew():
    return render_template(
        "whatsnew.html", title="Hva er nytt", year=datetime.now().year, **common_items()
    )


@app.route("/leaderboard")
def leaderboard():

    exercises = pd.read_sql(
        "select exercise_name from Exercise", dbfunc.getconnection()
    )["exercise_name"].tolist()

    return render_template(
        "leaderboard.html",
        title="Tabellene",
        year=datetime.now().year,
        exercises=exercises,
        **common_items(),
    )


@app.route("/teamstats")
def teamstats():

    return render_template("teamstats.html", title="Teamkamp")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@cache.cached(timeout=50, key_prefix="registration_and_player")
def get_registration_and_player():
    return (
        pd.read_sql("select * from Registration", dbfunc.getconnection()),
        pd.read_sql("select * from Pushupchallenge_user", dbfunc.getconnection()),
    )


@app.route("/data3")
def data3():
    return da.total(*get_registration_and_player())


@app.route("/data_today")
def data_today():
    return da.today(*get_registration_and_player())


@app.route("/data_yesterday")
def data_yesterday():
    return da.yesterday(*get_registration_and_player())


@app.route("/data_five")
def data_five():
    return da.five(*get_registration_and_player())


@app.route("/data_medals")
def data_medals():
    return da.medals(*get_registration_and_player())


@app.route("/data_max")
def data_max():
    return da.max_reps(*get_registration_and_player())


@app.route("/teamstats_data")
def teamstats_data():
    return da.teamstats(*get_registration_and_player())
