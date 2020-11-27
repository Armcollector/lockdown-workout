import pandas as pd


def add_player(df, player_df):
    """
    Args:
        df: add player_name to dataframe
    """

    df = df.merge(
        player_df[["id", "username"]], left_on="player_id", right_on="id"
    ).drop("id", axis=1)

    return df


def pivot_registration(df):
    """
    Pivot registration df and add sum_reps
    """

    df.pivot(index=["player_id", "dt"], columns="exercise_id", values="reps").fillna(0)
    df["sum_reps"] = df.sum(axis=1)

    df = df.reset_index()[["player_id", "dt", "sum_reps"]]

    return df


def medals(df, player_df):
    """Dataframe

    Args:
        df (Pandas dataframe): pandas dataframe with (at least) player_id, exercise_id and reps
        player_df (pd): pandas dataframe with player_id and username


    Returns:
        Dataframe with username, gold, silver, bronze and points
    """

    if df.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df = pivot_registration(df)

        df["rank"] = (
            df.groupby("dt")["sum_reps"].rank("min", ascending=False).astype(int)
        )
        df = df[df["rank"] <= 3]
        df = (
            df.groupby(["player_id", "rank"])
            .count()
            .reset_index()
            .pivot(index="player_id", columns="rank", values="dt")
            .fillna(0)
            .astype(int)
        )

        if 2 not in df.columns:
            df[2] = 0
        if 3 not in df.columns:
            df[3] = 0

        df["points"] = df[1] * 3 + df[2] * 2 + df[3]
        df = add_player(df, player_df)
        df = df[["username", 1, 2, 3, "points"]]

        table = df.to_json(orient="split", index=False)
    return table


def max_reps(df, player_df):

    if df.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df = pivot_registration(df)
        df = df.groupby("player_id").max()
        df = df.merge(player_df[["id", "username"]], left_on="player_id", right_on="id")
        df = df[["username", 0, 1, 2, 3, "sum_reps"]]

        table = df.to_json(orient="split", index=False)
    return table
