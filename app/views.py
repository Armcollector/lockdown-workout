"""
Routes and views for the flask application.
"""

from datetime import date, datetime, timedelta

import pandas as pd
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

import app.databasefunctions as dbfunc
import app.forms as forms
from app import app
from app.databasefunctions import upsert
from app.models import Pushupchallenge_user, Registration

from . import app, cache, db


def common_items():
    d = {}
    d["maintitle"] = app.config["MAINTITLE"]
    return d


@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    pass

    return render_template(
        f"{app.config['INSTANCE']}_index.html",
        title="Hjem",
        year=datetime.now().year,
        **common_items(),
    )


@app.route("/test")
def test():
    return render_template("test.html")


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
            reps=form.sit_reps.data,
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            1,
            player_id=current_user.id,
            reps=form.air_reps.data,
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            2,
            player_id=current_user.id,
            reps=form.push_reps.data,
            dt=datetime.strptime(form.dt.data, "%Y-%m-%d")
            + timedelta(days=form.day.data),
        )
        upsert(
            3,
            player_id=current_user.id,
            reps=form.pull_reps.data,
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

    return render_template(
        "leaderboard.html",
        title="Tabellene",
        year=datetime.now().year,
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

    df, player_df = get_registration_and_player()

    if df.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:

        df2 = df.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)
        df2 = df2.reset_index()
        df2 = df2.groupby("player_id").sum()
        df2.columns = ["sit ups", "air squats", "push ups", "pull ups", "total reps"]
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        )
        df2 = df2[
            ["username", "sit ups", "air squats", "push ups", "pull ups", "total reps"]
        ]

        table = df2.to_json(orient="split", index=False)

    return table


@app.route("/data_today")
def data_today():

    df, player_df = get_registration_and_player()

    df2 = df[df.dt == date.today()]

    if df2.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df2 = df2.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)
        df2 = df2.reset_index()
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        )
        df2.columns = [
            "player",
            "dt",
            "sit ups",
            "air squats",
            "push ups",
            "pull ups",
            "total reps",
            "id",
            "username",
        ]
        df2 = df2[
            ["username", "sit ups", "air squats", "push ups", "pull ups", "total reps"]
        ]

        table = df2.to_json(orient="split", index=False)

    return table


@app.route("/data_yesterday")
def data_yesterday():

    df, player_df = get_registration_and_player()

    df2 = df[df.dt == date.today() - timedelta(days=1)]

    if df2.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df2 = df2.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)
        df2 = df2.reset_index()
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        )
        df2.columns = [
            "player",
            "dt",
            "sit ups",
            "air squats",
            "push ups",
            "pull ups",
            "total reps",
            "id",
            "username",
        ]
        df2 = df2[
            ["username", "sit ups", "air squats", "push ups", "pull ups", "total reps"]
        ]

        table = df2.to_json(orient="split", index=False)

    return table


@app.route("/data_five")
def data_five():

    df, player_df = get_registration_and_player()

    df2 = df[df.dt >= pd.to_datetime(date.today() - timedelta(days=5))]

    if df2.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df2 = df2.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)
        df2 = df2.reset_index()
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        )
        df2.columns = [
            "player",
            "dt",
            "sit ups",
            "air squats",
            "push ups",
            "pull ups",
            "total reps",
            "id",
            "username",
        ]
        df2 = df2[
            ["username", "sit ups", "air squats", "push ups", "pull ups", "total reps"]
        ]
        df2 = df2.groupby("username").sum().reset_index()

        table = df2.to_json(orient="split", index=False)

    return table


@app.route("/data_medals")
def data_medals():
    df, player_df = get_registration_and_player()

    df2 = df

    if df2.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df2 = df2.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)

        df2 = df2.reset_index()[["player_id", "dt", "sum_reps"]]

        df2["rank"] = (
            df2.groupby("dt")["sum_reps"].rank("min", ascending=False).astype(int)
        )
        df2 = df2[df2["rank"] <= 3]
        df2 = (
            df2.groupby(["player_id", "rank"])
            .count()
            .reset_index()
            .pivot(index="player_id", columns="rank", values="dt")
            .fillna(0)
        )

        df2 = df2.astype(int)

        if 2 not in df2.columns:
            df2[2] = 0
        if 3 not in df2.columns:
            df2[3] = 0

        df2["points"] = df2[1] * 3 + df2[2] * 2 + df2[3]
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        ).drop("id", axis=1)
        df2 = df2[["username", 1, 2, 3, "points"]]

        table = df2.to_json(orient="split", index=False)
    return table


@app.route("/data_max")
def data_max():
    df, player_df = get_registration_and_player()

    if df.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df2 = df.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df2["sum_reps"] = df2.sum(axis=1)
        df2 = df2.reset_index()
        df2 = df2.groupby("player_id").max()
        df2 = df2.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        )
        df2 = df2[["username", 0, 1, 2, 3, "sum_reps"]]

        table = df2.to_json(orient="split", index=False)
    return table


@app.route("/teamstats_data")
def teamstats_data():
    df, player_df = get_registration_and_player()

    df2 = df.pivot(
        index=["player_id", "dt"], columns="exercise_id", values="reps"
    ).fillna(0)
    df2["sum_reps"] = df2.sum(axis=1)
    df2 = df2.reset_index()
    df2 = df2.merge(
        player_df[["id", "username", "team"]], left_on="player_id", right_on="id"
    ).drop(["player_id"], axis=1)
    df2["rank"] = (
        df2.groupby("team")["sum_reps"].rank("first", ascending=False).astype(int)
    )
    df2 = df2[df2["rank"] <= 3]
    df2 = df2.groupby("team").mean().round().astype(int).reset_index()
    df2 = df2[["team", 0, 1, 2, 3, "sum_reps"]]

    table = df2.to_json(orient="split", index=False)
    return table
